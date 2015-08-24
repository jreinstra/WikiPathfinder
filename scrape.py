from bs4 import BeautifulSoup
from urllib import urlopen

import grequests
import warnings
import time

source = "United_States"
destination = "Adolf_Hitler"

titles_by_title = {source:None}


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


def get_titles_at_level(source_title, source_html, destination_title, num_levels):
    titles = get_titles_from_html(source_html)
    
    if source_title == destination_title:
        print destination_title
        return True
    elif destination_title in titles:
        print source_title, ">", destination_title
        return True
    elif num_levels == 0:
        return False
    else:
        print source_title, ">"
        urls = [url_from_title(title) for title in titles]
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            step = 20
            save_index = 0
            html_by_title = {}
            for x in range(0, len(urls), step):
                print "Downloading %s-%s..." % (x, x+step),
                rs = [grequests.get(u) for u in urls[x:x+step]]
                results = grequests.map(rs, stream=False, size=step)
                for result in results:
                    if result:
                        html_by_title[titles[save_index]] = result.content
                        result.close()
                    save_index += 1
                del results
                print "Done"
                time.sleep(2.0)
            
        found_destination = False
        for title, html in html_by_title.items():
            found_destination = found_destination or get_titles_at_level(title, html, destination_title, num_levels - 1)
        return found_destination
    
html = urlopen(url_from_title(source))
print get_titles_at_level(source, html, destination, 1)