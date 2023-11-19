import logging

from unspoken.enitites.enums.task_status import TaskStatus
from unspoken.services import db
from unspoken.services.audio.converter import convert_to_mp3, convert_to_wav
from unspoken.services.queue.broker import celery
from unspoken.settings import settings

from .diarize_audio_task import diarize_audio
from .transcribe_audio_task import transcribe_audio

logger = logging.getLogger(__name__)


@celery.task(
    name='convert_audio',
    ignore_result=True,
    queue=settings.low_resource_demand_queue,
    routing_key='low.convert_audio',
)
def convert_audio(temp_file_id: int) -> None:
    logger.info('Converting audio to mp3 for temporary file: %s', temp_file_id)
    file = db.get_temp_file(temp_file_id)
    if not file:
        logger.warning('Not found temporary file with id: %s.', temp_file_id)
        return
    task = db.get_task(file.task_id)
    if not task:
        logger.error('Not found task for temporary file id: %s', temp_file_id)
        db.remove_temp_file(temp_file_id)
        return
    db.update_task(task, status=TaskStatus.processing)
    mp3_audio = convert_to_mp3(file.data)
    wav_audio = convert_to_wav(file.data)
    audio = db.create_audio(
        db.Audio(
            file_name=file.file_name,
            mp3_data=mp3_audio,
            wav_data=wav_audio,
        )
    )
    db.update_task(task, audio_id=audio.id)
    logger.info('Publish diarize audio task for task_id: %s', task.id)
    diarize_audio.delay(task.id)
    logger.info('Publishing transcribe audio task for task_id: %s', task.id)
    transcribe_audio.delay(task.id)
    logger.info('Removing temporary file id: %s', temp_file_id)
    db.remove_temp_file(temp_file_id)
    logger.info('Audio converted successfully.')
