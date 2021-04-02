from typing import Optional, Tuple
from rq import Worker, Queue, Connection
from requests import post

from .core import conn
from .settings import WORKER_TYPES, QUEUE_URL

from ...ml.gisalgo import inference, numpy2torch, parse, ssim


def create_worker(queues):
    assert all(map(lambda key: key in WORKER_TYPES, queues))

    with Connection(conn):
        worker = Worker(map(Queue, queues))
        worker.work(with_scheduler=True)


def get_file(url_pro: Optional[str]) -> bytes:
    return open(url_pro, "rb").read()  # TODO: Поддержка web запросов


def worker_processing(b0_file_1,
                      data_file_1,
                      data_file_2,
                      deltatime: int,
                      point: Tuple[float],
                      window_size: Tuple[int],
                      vicinity_size: Tuple[int]) -> dict:
    try:
        (lat, lon), velocity, mask = inference(data_file_1, data_file_2, b0_file_1, deltatime, point, window_size, vicinity_size, ssim, "cpu", sf=0.5)
        if mask:
            res = {"points": [[point[1], point[0]], [lon, lat]],
                   "velocity": velocity,
                   "error": None}
        else:
            res = {"points": [[0, 0], [0, 0]],
                   "velocity": 0,
                   "error": "Что-то про маску"}
    except AttributeError as e:
        if e == "0":
            res = {"points": [[0, 0], [0, 0]],
                   "velocity": 0,
                   "error": "Точка вышла заграницы"}
        elif e == "1":
            res = {"points": [[0, 0], [0, 0]],
                   "velocity": 0,
                   "error": "Слишком много шума"}
        else:
            res = {"points": [[0, 0], [0, 0]],
                   "velocity": 0,
                   "error": "Аааааа"}
    return res


def add_worker(task_type: Optional[str] = "low",
               *params, **kwargs) -> None:
    post(QUEUE_URL, json={"params": params, "kwargs": kwargs,
                          "task_type": task_type})


def big_worker(url_pro_1: Optional[str],
               url_pro_2: Optional[str],
               points: Tuple[Tuple[float]],
               deltatime: int,
               window_size: Tuple[int],
               vicinity_size: Tuple[int]) -> None:
    file_1 = get_file(url_pro_1)
    file_2 = get_file(url_pro_2)
    b0_file_1, data_file_1 = parse(file_1)
    b0_file_2, data_file_2 = parse(file_2)
    data_file_1, data_file_2 = numpy2torch(data_file_1, data_file_2)
    for point in points:
        add_worker(b0_file_1, data_file_1, data_file_2, deltatime, point, window_size, vicinity_size)
