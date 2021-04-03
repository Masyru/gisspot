from typing import Optional, Tuple, List
from rq import Worker, Queue, Connection, get_current_job
from os import path
from requests import post
from json import dumps

import sys
sys.path.append("../../")
from backend.worker.core import conn
from backend.worker.settings import WORKER_TYPES, QUEUE_URL, SERVER_URL

from backend.queue.services import add_task, get_vector_json
from ml.gisalgo import inference, numpy2torch, parse, ssim


def create_worker(queues: List[str]):
    assert all(map(lambda key: key in WORKER_TYPES, queues))

    with Connection(conn):
        worker = Worker(map(Queue, queues))
        worker.work(with_scheduler=True)


def get_file(url_pro: Optional[str]):
    return open(url_pro, "rb")  # TODO: Поддержка web запросов


def worker_processing(b0_file_1,
                      data_file_1,
                      data_file_2,
                      deltatime: int,
                      point: Tuple[float],
                      window_size: Tuple[int],
                      vicinity_size: Tuple[int]) -> dict:
    try:
        (lat, lon), velocity, mask = inference(data_file_1, data_file_2, b0_file_1, deltatime, point, window_size, vicinity_size, ssim, "cpu", sf=0.5, tpe="geo")
        if mask:
            res = {"points": [[point[1], point[0]], [lon, lat]],
                   "velocity": velocity,
                   "error": None}
        else:
            res = {"points": [[0, 0], [0, 0]],
                   "velocity": 0,
                   "error": "Что-то про маску"}
    except AssertionError as e:
        e = e.args[0]
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


def add_worker(ws_id: Optional[str], task_type: Optional[str],
               *params, **kwargs) -> None:
    add_task(task_type=task_type, ws_id=ws_id, args=params, kwargs=kwargs)
    # post(QUEUE_URL, json={"params": params, "kwargs": kwargs,
    #                       "task_type": task_type})


def normalize(file_path) -> str:
    disk, main_path = file_path.split(":")
    disk = disk.lower()
    return "/mnt/" + disk + main_path.replace("\\", "/")


def big_worker(ws_id: Optional[str],
               url_pro_1: Optional[str],
               url_pro_2: Optional[str],
               points: Tuple[Tuple[float]],
               deltatime: int,
               window_size: Tuple[int],
               vicinity_size: Tuple[int]) -> None:
    """
    Функция для первого этапа обработки

    :param ws_id: Id ws, который закинул задачу
    :param url_pro_1: Путь до первого .tiff файла
    :param url_pro_2: Путь до второго .tiff файла
    :param points: Tuple точек в гео координатах, (lat, lon)
    :param deltatime: Разница в сек. между снимками
    :param window_size: Что-то про размер окна
    :parma vicinity_size: Какой-то ещё рзмер
    """
    file_1 = get_file(normalize(url_pro_1))
    file_2 = get_file(normalize(url_pro_2))
    b0_file_1, data_file_1 = parse(file_1)
    b0_file_2, data_file_2 = parse(file_2)
    data_file_1, data_file_2 = numpy2torch(data_file_1, data_file_2)
    for point in points:
        # print(worker_processing(b0_file_1, data_file_1,data_file_2, deltatime, point, window_size, vicinity_size))
        add_worker(ws_id, "default", b0_file_1, data_file_1, data_file_2, deltatime, point, window_size, vicinity_size)


def send_result():
    job = get_current_job(conn)
    result = get_vector_json(job.dependency_ids[0].decode("utf-8").split(":")[-1])
    post(SERVER_URL, data=dumps(result))
