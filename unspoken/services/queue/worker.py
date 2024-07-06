from .tasks import transcribe
from .broker import celery

worker = celery
worker.register_task(transcribe)
