from bs4 import BeautifulSoup

import grequests
import warnings
import time

MAX_CONC_ARTICLES = 20

def url_from_title(title):
    return "http://en.wikipedia.org/wiki/" + title

def get_titles_from_html(html):
    article = BeautifulSoup(html, 'html.parser')
    titles = []
    for a in article.find_all('a'):
        href = a.get("href")
        if href:
            if href[:6] == "/wiki/" and not ":" in href and not href[6:] in titles:
                titles.append(href[6:])
    return titles

def load_pages_from_titles(titles):
    urls = [url_from_title(title) for title in titles]
        
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        save_index = 0
        html_by_title = {}
        for x in range(0, len(urls), MAX_CONC_ARTICLES):
            print ("Downloading %s-%s..." % (x, x+MAX_CONC_ARTICLES)),
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