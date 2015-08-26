from django.shortcuts import render
from django.http import HttpResponse

from rq import Queue
from rq.job import Job
from tasks.worker import conn

import json

from utils import *

# Create your views here.
def find(request):
    q = Queue(connection=conn)
    
    result = []
    source_title = request.GET.get("source")
    destination_title = request.GET.get("destination")
    if source_title and destination_title:
        source_article = article_from_title(source_title)
        level = 0
        """result = []
        while len(result) == 0:
            paths = get_paths_at_level(source_article, destination_title, level)
            result += paths
            level += 1"""
        job = q.enqueue(get_paths_at_level, source_article, destination_title, 3)
        return json_success(job.get_id())
    else:
        return json_failure("missing 'source' or 'destination' parameters")
    
def check(request):
    job_id = request.GET.get("job_id")
    if job_id:
        job = Job.fetch(job_id, connection=conn)
        if job.is_finished:
            return json_success(job.result)
        else:
            return json_success("In progress")
    else:
        return json_failure("missing 'job_id' parameter")
    
def json_success(data):
    return HttpResponse(json.dumps({"success":True, "result":data}))
                        
def json_failure(error):
    return HttpResponse(json.dumps({"success":False, "error":error}))