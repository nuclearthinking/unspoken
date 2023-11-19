from .broker import celery
from .tasks import complete_transcription
from .tasks import convert_audio
from .tasks import diarize_audio
from .tasks import speach_to_text

worker = celery
worker.register_task(complete_transcription)
worker.register_task(speach_to_text)
worker.register_task(diarize_audio)
worker.register_task(convert_audio)
