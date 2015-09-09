# imports for django methods
from django.shortcuts import render
from django.http import HttpResponse

# imports related to background task queue
from rq import Queue
from rq.job import Job, JobStatus
from worker import conn

# imports for utilities
import json
import uuid

# import article-finding methods
from utils import *

# Create your views here.
def find(request):
    """Creates a background process to find the shortest distance between two
    articles and returns the id of the process.
    """
    # get worker queue
    q = Queue(connection=conn)
    
    # validate GET parameters
    result = []
    source_title = request.GET.get("source")
    destination_title = request.GET.get("destination")
    if source_title and destination_title:
        # enqueue job with 5000-sec timeout and return job id
        job_id = str(uuid.uuid4())
        job = q.enqueue_call(
            func=get_paths,
            args=(source_title, destination_title, job_id,),
            timeout=5000,
            job_id=job_id
        )
        return json_success(job_id)
    else:
        return json_failure("missing 'source' or 'destination' parameters")
    
def check(request):
    """Takes the provided job id for a background process and returns the
    status and result, if applicable.
    """
    # validate GET parameter
    job_id = request.GET.get("job_id")
    if job_id:
        # try to get job from id
        try:
            job = Job.fetch(job_id, connection=conn)
        except Exception:
            job = None
        if job:
            # return job status and output
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
    """Converts the provided data into JSON and puts it in a standardized
    success message.
    """
    return HttpResponse(json.dumps({"success":True, "result":data}))
                        
def json_failure(error):
    """Converts the provided data into JSON and puts it in a standardized
    failure message.
    """
    return HttpResponse(json.dumps({"success":False, "error":error}))