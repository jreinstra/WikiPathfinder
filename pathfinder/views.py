from django.shortcuts import render
from django.http import HttpResponse

from urllib import urlopen

import json

from utils import *

# Create your views here.
def index(request):
    result = []
    source = request.GET.get("source")
    destination = request.GET.get("destination")
    if source and destination:
        source_html = urlopen(url_from_title(source))
        found = False
        level = 0
        while not found:
            paths = get_paths_at_level(source, source_html, destination, level, "")
            result.append(paths)
            found = found or len(paths) > 0
            level += 1
    else:
        return json_failure("missing 'source' or 'destination' parameters")
    
def json_success(data):
    return HttpResponse(json.dumps({"success":True, "result":data}))
                        
def json_failure(error):
    return HttpResponse(json.dumps({"success":False, "error":error}))