from rq import Queue
from worker import conn

from pathfinder.utils import *

q = Queue(connection=conn)