from bs4 import BeautifulSoup
from urllib import urlopen

# RQ stuff
from worker import conn
from rq.job import Job

# imports for utilities
import grequests
import warnings
import time
import json

from models import Article

MAX_CONC_ARTICLES = 20
BANNED_ARTICLES = ["Main_Page"]

def article_from_title(title):
    """Finds or creates an article model from the given title and returns
    the object.
    """
    article = Article.objects.filter(title=title)
    if article.count() != 1:
        # Case 1: No articles match title, so create a new article
        article = Article(title=title, downloaded=False, filled=False)
        article.save()
    else:
        # Case 2: Article(s) match title, so take the first result
        article = article[0]
    return article

def url_from_title(title):
    """Returns the url for a wikipedia article with the given title."""
    return "http://en.wikipedia.org/wiki/" + title

def get_titles_from_html(html):
    """Parses provided HTML for wikipedia links and returns list of titles."""
    article_html = BeautifulSoup(html, 'html.parser')
    titles = []
    # loop through all links that parser finds
    for a in article_html.find_all('a'):
        href = a.get("href")
        if href:
            new_title = href[6:]
            if(
                href[:6] == "/wiki/" and
                not ":" in href and
                not new_title in BANNED_ARTICLES and
                not new_title in titles
            ):
                # add new title if it's a valid wikipedia article
                titles.append(new_title)
    return titles

def load_pages_from_titles(titles, job):
    """Sends batch requests to download articles from given list of titles and
    returns result.
    """
    urls = [url_from_title(title) for title in titles]
        
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        save_index = 0
        html_by_title = {}
        for x in range(0, len(urls), MAX_CONC_ARTICLES):
            # update job status
            update_string = "Downloading %s-%s of %s..." % (
                x,
                x+MAX_CONC_ARTICLES,
                len(urls)
            )
            if job:
                job.set_status(update_string)
            print (update_string)
            
            # send requests in parallel batches of 20
            rs = [grequests.get(u) for u in urls[x:x+MAX_CONC_ARTICLES]]
            results = grequests.map(rs, stream=False, size=MAX_CONC_ARTICLES)
            # save results by title
            for result in results:
                if result:
                    html_by_title[titles[save_index]] = result.content
                    result.close()
                save_index += 1
            del results
            print "Done"
            # sleep to not overload wikipedia
            time.sleep(2.0)
            
    return html_by_title

def download_all_linked_articles(titles, job):
    """Downloads all of the articles in the provided list of titles."""
    articles = [article_from_title(title) for title in titles]
    # only gets un-downloaded titles
    titles = [
        str(article) for
        article in articles if
        article.downloaded == False
    ]
    # sends the batch http requests
    html_by_title = load_pages_from_titles(titles, job)
    
    length = len(html_by_title.items())
    i = 1
    # update article models with new data
    for article_title, article_html in html_by_title.items():
        article_titles = get_titles_from_html(article_html)
        update_article(article_title, article_titles)
        # update job status
        if i % 20 == 0:
            update_string = "Updated %s-%s of %s" % (i-20, i, length)
            if job:
                job.set_status(update_string)
            print update_string
        i += 1
        
def update_article(article_title, titles):
    """Updates an article models with its linked titles."""
    article = article_from_title(article_title)
    # saved as string - JSON list
    article.linked_articles = json.dumps(titles)
    article.downloaded = True
    article.save()
            
def get_paths_at_level(source, destination_title, num_levels, job):
    """Returns all possible paths up to a specific level."""
    if not source.downloaded:
        # download article and populate storage model if not downloaded
        source_html = urlopen(url_from_title(source.title))
        update_article(source, get_titles_from_html(source_html))
        source = article_from_title(source.title)
    
    source_titles = json.loads(source.linked_articles)
    if num_levels == 0:
        # Case 1: Don't go any levels deeper
        source_titles = json.loads(source.linked_articles)
        if source.title == destination_title:
            return [source.title]
        elif destination_title in source_titles:
            return [source.title + " > " + destination_title]
        else:
            return []
    else:
        # Case 2: Go 1 or more levels further
        if not source.filled:
            # Case 2b: Download linked articles if not downloaded yet
            download_all_linked_articles(source_titles, job)
            source.filled = True
            source.save()
            
        result_paths = []
        length = len(source_titles)
        i = 1
        # check if any linked articles match destination title
        for title in source_titles:
            article = article_from_title(title)
            paths = get_paths_at_level(
                article,
                destination_title,
                num_levels - 1,
                None
            )
            for path in paths:
                # add current article title to result paths
                result_paths.append((source.title + " > " + path))
            if job and num_levels >= 2:
                # update status of background job
                percent_done = (100.0 * i) / length
                job.set_status(
                    "%.2f%% done with level %s" % (
                        percent_done,
                        num_levels
                    )
                )
                print num_levels, "-", ("%s of %s" % (i, length)), title
            i += 1
        return result_paths
    
def get_paths(source_title, destination_title, job_id):
    """Returns a list of the shortest paths between two articles."""
    job = Job.fetch(job_id, connection=conn)
    source = article_from_title(source_title)
    levels = 0
    result = []
    # keep looking at progressively higher levels until paths are found
    while len(result) == 0 and levels < 3:
        paths = get_paths_at_level(source, destination_title, levels, job)
        result += paths
        print "Looked at level %s." % levels
        levels += 1
    return result
    