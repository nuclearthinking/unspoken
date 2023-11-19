import datetime
import logging
from datetime import timezone

import torch

from unspoken.enitites.enums.task_status import TaskStatus
from unspoken.services import db
from unspoken.services.ml.diarizer import Diarizer
from unspoken.services.queue.broker import celery
from unspoken.settings import settings

logger = logging.getLogger(__name__)


@celery.task(
    name='diarize_audio',
    ignore_result=True,
    queue=settings.high_resource_demand_queue,
    routing_key='high.diarize_audio',
    bind=True,
    max_retries=5,
)
def diarize_audio(self, task_id: int):
    torch.cuda.empty_cache()
    logger.info('Diarizing audio for task_id: %s', task_id)
    task = db.get_task(task_id)
    if not task:
        logger.warning('Not found task with id: %s', task_id)
        return
    if task.audio is None:
        logger.error('Task with id: %s has no audio, therefore cannot be transcribed.', task_id)
        db.update_task(task, status=TaskStatus.failed)
        return
    diarization_result = None
    try:
        diarization_result = Diarizer().diarize_audio(task.audio.wav_data)
    except torch.cuda.OutOfMemoryError as e:
        logger.exception('Cuda out of memory error occurred for task_id: %s, retrying.', task_id)
        torch.cuda.empty_cache()
        self.retry(exc=e, countdown=5)
    except RuntimeError as e:
        logger.exception('Diarizer failed for task_id: %s, retrying.', task_id)
        self.retry(exc=e, countdown=5)
    except Exception as e:
        logger.error('Failed to diarize audio for task_id: %s', task_id, exc_info=e)
        db.update_task(task, status=TaskStatus.failed, updated_at=datetime.datetime.now(timezone.utc))
        return
    if not diarization_result:
        logger.error('Empty diarization result!')
        return
    db.save_diarization_result(task.transcript_id, diarization_result.dict())
    logger.info('Finished diarizing audio for task_id: %s', task_id)
