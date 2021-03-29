from rq.command import send_stop_job_command
from rq.job import Job
from typing import Optional, List
from main import queues

from backend.queue.settings import TTL, RESULT_TTL, FAILURE_TTL


def add_task(func, args: Optional[tuple],
             kwargs: Optional[dict],
             ws_id: int,
             task_type="default") -> None:
    assert task_type in queues.keys()
    meta = {"ws_id": ws_id}
    queues[task_type].enqueue_call(func=func, args=args,
                                   kwargs=kwargs, meta=meta,
                                   result_ttl=RESULT_TTL,
                                   failure_ttl=FAILURE_TTL,
                                   ttl=TTL)


def stop_all_ws_task(ws_id: int) -> None:
    for queue in queues.values():
        for job in queue.jobs:
            if job.meta["ws_id"] == ws_id:
                send_stop_job_command(queue, job.id)


def get_all_result_task(queue_type: Optional[str] = "default") -> List[Job]:
    assert queue_type in queues.keys()

    jobs_result: List[Job] = []
    for job in queues[queue_type].jobs:
        job: Job
        if job.result is not None:
            jobs_result.append(job)

    return jobs_result
