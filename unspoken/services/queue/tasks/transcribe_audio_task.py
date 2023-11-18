import logging

from unspoken.enitites.enums.task_status import TaskStatus
from unspoken.services import db
from unspoken.services.ml.transcriber import TranscriberFactory
from unspoken.services.queue.broker import celery

logger = logging.getLogger(__name__)


@celery.task(name='transcribe_audio')
def transcribe_audio(task_id: int):
    logger.info('Transcribing audio for task_id: %s', task_id)
    task = db.get_task(task_id)
    if not task:
        logger.warning('Not found task with id: %s', task_id)
        return
    if task.audio is None:
        logger.error('Task with id: %s has no audio, therefore cannot be transcribed.', task_id)
        db.update_task(task, status=TaskStatus.failed)
        return
    db.update_task(task, status=TaskStatus.transcribing)
    transcript = TranscriberFactory.get_transcriber().transcribe(task.audio.mp3_data)
    logger.info('Finished transcribing audio for task_id: %s, transcript %s', task_id, transcript)
    logger.info('Finished transcribing audio for task_id: %s', task_id)
