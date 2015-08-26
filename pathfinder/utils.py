from bs4 import BeautifulSoup
from urllib import urlopen

import grequests
import warnings
import time
import json

from models import Article

MAX_CONC_ARTICLES = 20
BANNED_ARTICLES = ["Main_Page"]

def article_from_title(title):
    article = Article.objects.filter(title=title)
    if article.count() != 1:
        article = Article(title=title, downloaded=False)
        article.save()
    else:
        article = article[0]
    return article

def url_from_title(title):
    return "http://en.wikipedia.org/wiki/" + title

def get_titles_from_html(html):
    article_html = BeautifulSoup(html, 'html.parser')
    titles = []
    for a in article_html.find_all('a'):
        href = a.get("href")
        if href:
            new_title = href[6:]
            if href[:6] == "/wiki/" and not ":" in href and not new_title in BANNED_ARTICLES and not new_title in titles:
                titles.append(new_title)
    return titles

def load_pages_from_titles(titles):
    urls = [url_from_title(title) for title in titles]
        
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        save_index = 0
        html_by_title = {}
        for x in range(0, len(urls), MAX_CONC_ARTICLES):
            print ("Downloading %s-%s of %s..." % (x, x+MAX_CONC_ARTICLES, len(urls)))
            rs = [grequests.get(u) for u in urls[x:x+MAX_CONC_ARTICLES]]
            results = grequests.map(rs, stream=False, size=MAX_CONC_ARTICLES)
            for result in results:
                if result:
                    html_by_title[titles[save_index]] = result.content
                    result.close()
                save_index += 1
            del results
            print "Done"
            time.sleep(2.0)
            
    return html_by_title

def download_all_linked_articles(titles):
    articles = [article_from_title(title) for title in titles]
    titles = [str(article) for article in articles if article.downloaded == False]
    html_by_title = load_pages_from_titles(titles)
    
    length = len(html_by_title.items())
    i = 1
    for article_title, article_html in html_by_title.items():
        article_titles = get_titles_from_html(article_html)
        update_article(article_title, article_titles)
        if i % 20 == 0:
            print "Updated %s-%s of %s" % (i-20, i, length)
        i += 1
        
def update_article(article_title, titles):
    article = article_from_title(article_title)
    article.linked_articles = json.dumps(titles)
    article.downloaded = True
    article.save()
            
def get_paths_at_level(source, destination_title, num_levels):
    if not source.downloaded:
        source_html = urlopen(url_from_title(source.title))
        update_article(source, get_titles_from_html(source_html))
        source = article_from_title(source.title)
        
    source_titles = json.loads(source.linked_articles)
    
    if source.title == destination_title:
        return [source.title]
    elif destination_title in source_titles:
        return [source.title + " > " + destination_title]
    elif num_levels == 0:
        return []
    else:
        download_all_linked_articles(source_titles)
        result_paths = []
        for title in source_titles:
            article = article_from_title(title)
            paths = get_paths_at_level(article, destination_title, num_levels - 1)
            for path in paths:
                result_paths.append((source.title + " > " + path))
        return result_paths
    