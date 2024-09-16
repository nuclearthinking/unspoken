import queue
import threading
from typing import Callable

import logging

logger = logging.getLogger('uvicorn')

task_queue = queue.Queue()


def worker(process_func: Callable):
    while True:
        task = task_queue.get()
        if task is None:
            break
        try:
            process_func(*task)
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
