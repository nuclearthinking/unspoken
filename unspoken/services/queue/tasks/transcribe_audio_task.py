import logging
import datetime
from datetime import timezone

import torch

from unspoken.services import db
from unspoken.settings import settings
from unspoken.services.queue.broker import celery
from unspoken.services.ml.transcriber import Transcriber
from unspoken.enitites.enums.task_status import TaskStatus

logger = logging.getLogger(__name__)


@celery.task(
    name='speach_to_text',
    ignore_result=True,
    queue=settings.high_resource_demand_queue,
    routing_key='high.speach_to_text',
    bind=True,
    max_retries=5,
)
def speach_to_text(self, task_id: int):
    torch.cuda.empty_cache()
    logger.info('Transcribing audio for task_id: %s', task_id)
    task = db.get_task(task_id)
    if not task:
        logger.warning('Not found task with id: %s', task_id)
        return
    if task.audio is None:
        logger.error('Task with id: %s has no audio, therefore cannot be transcribed.', task_id)
        db.update_task(task, status=TaskStatus.failed)
        return
    transcription_result = None
    try:
        transcription_result = Transcriber().transcribe(task.audio.mp3_data)
    except RuntimeError as e:
        logger.exception('Transcriber failed for task_id: %s, retrying.', task_id)
        self.retry(exc=e, countdown=5)
    except Exception as e:
        logger.error('Failed to transcribe audio for task_id: %s', task_id, exc_info=e)
        db.update_task(task, status=TaskStatus.failed, updated_at=datetime.datetime.now(timezone.utc))
        return
    if not transcription_result:
        logging.error('Emtpy transcription result!')
        return
    db.save_speach_to_text_result(task.transcript_id, transcription_result.dict())
    logger.info('Checking is task completed for task_id %s.', task_id)
    celery.send_task(
        name='complete_transcription',
        args=(task_id,),
        queue=settings.low_resource_demand_queue,
        routing_key='low.complete_transcription',
    )
    logger.info('Finished transcribing audio for task_id: %s', task_id)
