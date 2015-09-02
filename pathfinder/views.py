from django.shortcuts import render
from django.http import HttpResponse

from rq import Queue
from rq.job import Job, JobStatus
from tasks.worker import conn

import json
import uuid

from utils import *

# Create your views here.
def find(request):
    q = Queue(connection=conn)
    
    result = []
    source_title = request.GET.get("source")
    destination_title = request.GET.get("destination")
    if source_title and destination_title:
        job_id = uuid.uuid4()
        job = q.enqueue_call(
            func=get_paths,
            args=(source_title, destination_title, job_id,),
            timeout=5000
        )
        return json_success(job_id)
    else:
        return json_failure("missing 'source' or 'destination' parameters")
    
def check(request):
    job_id = request.GET.get("job_id")
    if job_id:
        try:
            job = Job.fetch(job_id, connection=conn)
        except Exception:
            job = None
        if job:
            status = job.get_status()
            if status == JobStatus.FINISHED:
                return json_success({"status":status, "output":job.result})
            else:
                return json_success({"status":status, "output":None})
        else:
            return json_failure("job not found")
    else:
        return json_failure("missing 'job_id' parameter")
    
def json_success(data):
    return HttpResponse(json.dumps({"success":True, "result":data}))
                        
def json_failure(error):
    return HttpResponse(json.dumps({"success":False, "error":error}))