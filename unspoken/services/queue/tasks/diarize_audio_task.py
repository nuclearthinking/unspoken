import logging

from unspoken.enitites.enums.task_status import TaskStatus
from unspoken.services import db
from unspoken.services.ml.diarizer import Diarizer
from unspoken.services.queue.broker import celery

logger = logging.getLogger(__name__)


@celery.task(name='diarize_audio')
def diarize_audio(task_id: int):
    logger.info('Diarizing audio for task_id: %s', task_id)
    task = db.get_task(task_id)
    if not task:
        logger.warning('Not found task with id: %s', task_id)
        return
    if task.audio is None:
        logger.error('Task with id: %s has no audio, therefore cannot be transcribed.', task_id)
        db.update_task(task, status=TaskStatus.failed)
        return
    try:
        diarization_result = Diarizer().diarize_audio(task.audio.wav_data)
    except Exception as e:
        logger.error('Failed to diarize audio for task_id: %s', task_id, exc_info=e)
        db.update_task(task, status=TaskStatus.failed)
        return
    logger.info('Finished diarizing audio for task_id: %s', task_id)
    db.save_diarization_result(task.transcript_id, diarization_result.dict())
