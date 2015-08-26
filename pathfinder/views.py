from django.shortcuts import render
from django.http import HttpResponse

import json

from utils import *

# Create your views here.
def index(request):
    result = []
    source_title = request.GET.get("source")
    destination_title = request.GET.get("destination")
    if source_title and destination_title:
        level = 0
        result = []
        while len(result) == 0:
            source_article = article_from_title(source_title)
            paths = get_paths_at_level(source_article, destination_title, level)
            result += paths
            level += 1
        return json_success(result)
    else:
        return json_failure("missing 'source' or 'destination' parameters")
    
def json_success(data):
    return HttpResponse(json.dumps({"success":True, "result":data}))
                        
def json_failure(error):
    return HttpResponse(json.dumps({"success":False, "error":error}))