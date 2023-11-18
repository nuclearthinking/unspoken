from .broker import celery
from .tasks import convert_audio, transcribe_audio

worker = celery
worker.register_task(transcribe_audio)
worker.register_task(convert_audio)
