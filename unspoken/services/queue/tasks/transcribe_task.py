import logging

from unspoken.settings import settings
from unspoken.services.queue.broker import celery
from unspoken.services.queue.pipelines.transcribe_flow import transcribe_audio_flow

logger = logging.getLogger(__name__)


@celery.task(
    name='transcribe',
    ignore_result=True,
    queue=settings.transcribe_audio_queue,
    routing_key=settings.transcribe_audio_routing_key,
    bind=True,
    max_retries=5,
)
def transcribe(task, temp_file_id: int, task_id: int):
    logger.info('Processing queue task %s. Transcribing task %s started.', task, task_id)
    transcribe_audio_flow(temp_file_id, task_id)
    logger.info('Transcribing task %s completed.', task_id)
