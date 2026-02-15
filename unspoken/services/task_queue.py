import logging
import queue
import threading
import time
from typing import Callable

logger = logging.getLogger('uvicorn')

task_queue = queue.Queue()


def worker(process_func: Callable):
    logger.info('Background worker is running and waiting for tasks.')
    while True:
        task = task_queue.get()
        if task is None:
            logger.info('Background worker received shutdown signal.')
            break
        started_at = time.perf_counter()
        logger.info('Background worker picked up task payload: %s', task)
        try:
            process_func(*task)
            logger.info('Background worker finished task in %.2fs.', time.perf_counter() - started_at)
        except Exception as e:
            logger.exception(f'Error processing task: {e}')
        finally:
            task_queue.task_done()


def start_worker(process_func: Callable):
    thread = threading.Thread(target=worker, args=(process_func,))
    thread.start()
    return thread


def stop_worker():
    task_queue.put(None)


def add_task(*args):
    task_queue.put(args)
