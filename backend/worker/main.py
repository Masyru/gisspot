from backend.worker.services import create_worker
from backend.worker.settings import WORKER_TYPES

if __name__ == '__main__':
    create_worker(WORKER_TYPES)
