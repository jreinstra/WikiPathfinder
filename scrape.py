from pathfinder.utils import *

from urllib import urlopen

source = "Menlo_School"
destination = "Kevin_Bacon"

def get_paths_at_level(source_title, source_html, destination_title, num_levels):
    titles = get_titles_from_html(source_html)
    
    if source_title == destination_title:
        return [source_title]
    elif destination_title in titles:
        return [source_title + " > " + destination_title]
    elif num_levels == 0:
        return []
    else:
        html_by_title = load_pages_from_titles(titles)
            
        result_paths = []
        for title, html in html_by_title.items():
            paths = get_paths_at_level(title, html, destination_title, num_levels - 1)
            for path in paths:
                result_paths.append((source_title + " > " + path))
        return result_paths
    
html = urlopen(url_from_title(source))
paths = get_paths_at_level(source, html, destination, 1)
print "\n".join(paths)
print len(paths)