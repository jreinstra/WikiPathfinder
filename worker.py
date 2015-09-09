from wiki.wsgi import *
import os

import redis
from rq import Worker, Queue, Connection

# listen to jobs on 3 queues
listen = ['high', 'default', 'low']

# get environment variable for Redis database or default to localhost
redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

# start worker process
if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()