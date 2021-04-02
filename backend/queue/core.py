from rq import Queue
from redis import from_url

from .settings import REDIS_URL

__all__ = ["queues"]

redis_conn = from_url(REDIS_URL)
queues = {"default": Queue("default", connection=redis_conn),
          "high": Queue("high", connection=redis_conn)}
tasks = {"default": ".worker_processing",
         "high": ".big_worker"}
