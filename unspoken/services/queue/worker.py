from .tasks import convert_audio, diarize_audio, speach_to_text, complete_transcription
from .broker import celery

worker = celery
worker.register_task(complete_transcription)
worker.register_task(speach_to_text)
worker.register_task(diarize_audio)
worker.register_task(convert_audio)
