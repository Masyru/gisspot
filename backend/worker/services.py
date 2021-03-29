from typing import Optional, Tuple
from rq import Worker, Queue, Connection

from backend.worker.core import conn
from backend.worker.settings import WORKER_TYPES


def create_worker(queues):
    assert all(map(lambda key: key in WORKER_TYPES, queues))

    with Connection(conn):
        worker = Worker(map(Queue, queues))
        worker.work(with_scheduler=True)


def get_file(url_pro: Optional[str]) -> bytes:
    pass


def worker_processing(url_pro_1: Optional[str],
                      url_pro_2: Optional[str],
                      point: Tuple[float, float],
                      ws_id: Optional[int],
                      window_size: Tuple[float, float],
                      vicinity_size: Tuple[float, float]) -> dict:
    file_1 = get_file(url_pro_1)
    file_2 = get_file(url_pro_2)
    b0_file_1, data_file_1 = parse(file_1)
    b0_file_2, data_file_2 = parse(file_2)

    file_1, file_2 = numpy2torch(data_file_1, data_file_2)
    try:
        pos, score, _, _ = find_best_match(file_1, file_2, (point[1], point[0]), window_size, vicinity_size)
        speed = calculate_distance(b0_file_1, point, pos)
        return {"x1": point[1], "y1": point[0],
                "x2": pos[1], "y2": pos[0],
                "speed": speed,
                "error_message": None}
    except AttributeError as e:
        return {"x1": 0, "y1": 0,
                "x2": 0, "y2": 0,
                "speed": 0,
                "error_message": e}
