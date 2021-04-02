from .services import get_all_result_task, send_vector

if __name__ == '__main__':
    olds = []
    while True:
        jobs = get_all_result_task()
        for job in jobs:
            if job.id in olds:
                continue
            olds.append(job.id)
            send_vector(job)
