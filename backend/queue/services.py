from rq.command import send_stop_job_command
from rq.job import Job
from typing import Optional, List
from core import queues, tasks
from requests import post

from settings import TTL, RESULT_TTL, FAILURE_TTL, SERVER_URL


def add_task(args: Optional[tuple],
             kwargs: Optional[dict],
             ws_id: Optional[str],
             task_type: Optional[str] = "default") \
        -> None:
    assert task_type in queues.keys()
    meta = {"ws_id": ws_id}
    # if task_type == "default":  # TODO : Добавить worker, который будет возращать ответ серверу
        # queues[task_type].enqueue("")
    queues[task_type].enqueue_call(func=tasks[task_type], args=args,
                                   kwargs=kwargs, meta=meta,
                                   result_ttl=RESULT_TTL,
                                   failure_ttl=FAILURE_TTL,
                                   ttl=TTL)


def stop_all_ws_task(ws_id: str) -> None:
    for queue in queues.values():
        for job in queue.jobs:
            if job.meta["ws_id"] == ws_id:
                send_stop_job_command(queue, job.id)


def get_all_result_task(queue_type: Optional[str] = "default") \
        -> List[Job]:
    assert queue_type in queues.keys()

    jobs_result: List[Job] = []
    for job in queues[queue_type].jobs:
        job: Job
        if job.result is not None:
            jobs_result.append(job)

    return jobs_result


def preparing_vector_json(job: Job) -> dict:
    result = job.result
    result["ws_id"] = job.meta["ws_id"]
    return result


def send_vector(job: Job) -> None:
    post(SERVER_URL, json=preparing_vector_json(job))
