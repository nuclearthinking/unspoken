import uuid
import logging

from unspoken.services import db
from unspoken.settings import settings
from unspoken.services.queue.broker import celery
from unspoken.services.audio.converter import convert_to_wav
from unspoken.enitites.enums.mime_types import MimeType
from unspoken.enitites.enums.task_status import TaskStatus

logger = logging.getLogger(__name__)


@celery.task(
    name='convert_audio',
    ignore_result=True,
    queue=settings.low_resource_demand_queue,
    routing_key='low.convert_audio',
)
def convert_audio(temp_file_id: int, task_id: int) -> None:
    logger.info('Converting audio to mp3 for temporary file: %s', temp_file_id)

    temp_file = db.get_temp_file(temp_file_id)
    if not temp_file:
        logger.warning('Not found temporary file with id: %s.', temp_file_id)
        return

    task = db.get_task(task_id)
    if not task:
        logger.error('Not found task for temporary file id: %s', temp_file_id)
        temp_file.delete()
        return

    wav_temp_file = None
    try:
        db.update_task(task, status=TaskStatus.conversion)

        temp_file_data = temp_file.read()

        wav_audio_data = convert_to_wav(temp_file_data)
        wav_temp_file = db.save_temp_file(db.TempFile(file_name=uuid.uuid4(), file_type=MimeType.wav))
        wav_temp_file.write(wav_audio_data)
        logger.info('Saved temp audio %s', wav_temp_file)
        db.update_task(task, wav_file_id=wav_temp_file.id)

        task = db.get_task(task_id)
        logger.info('Publish diarize audio task for task_id: %s', task.id)
        celery.send_task(
            name='diarize_audio',
            args=(task.id,),
            queue=settings.high_resource_demand_queue,
            routing_key='high.diarize_audio',
        )
        logger.info('Publishing transcribe audio task for task_id: %s', task.id)
        celery.send_task(
            name='speach_to_text',
            args=(task.id,),
            queue=settings.high_resource_demand_queue,
            routing_key='high.speach_to_text',
        )
        logger.info('Audio converted successfully.')
    except Exception:
        logger.exception('Exception occurred while converting audio file')
        db.update_task(task, staus=TaskStatus.failed)
        if wav_temp_file is not None:
            logger.info('Deleting wav file: %s', wav_temp_file.file_name)
            wav_temp_file.delete()
    finally:
        logger.info('Removing temporary file id: %s', temp_file_id)
        temp_file.delete()
