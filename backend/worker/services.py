from rq import Worker, Queue, Connection

from backend.worker.core import conn
from backend.worker.settings import WORKER_TYPES


def create_worker(queues):
    assert all(map(lambda key: key in WORKER_TYPES, queues))

    with Connection(conn):
        worker = Worker(map(Queue, queues))
        worker.work(with_scheduler=True)
