from wiki.wsgi import *
# start script

from pathfinder.utils import *
from pathfinder.models import Article

source = Article.objects.get_or_create(title="Menlo_School")[0]
destination = "Kevin_Bacon"
    
paths = get_paths_at_level(source, destination, 2)
print "\n".join(paths)
print len(paths)