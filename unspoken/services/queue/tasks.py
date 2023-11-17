import logging

from celery import Celery

from unspoken.enitites.enums.task_status import TaskStatus
from unspoken.services import db
from unspoken.services.audio.converter import convert_to_mp3, convert_to_wav
from unspoken.services.ml.transcriber import TranscriberFactory
from unspoken.settings import settings

logger = logging.getLogger(__name__)

broker_url = 'amqp://{user}:{password}@{host}:{port}{vhost}'.format(
    user=settings.rabbitmq_user,
    password=settings.rabbitmq_password,
    host=settings.rabbitmq_host,
    port=settings.rabbitmq_port,
    vhost=settings.rabbitmq_vhost,
)

celery = Celery('unspoken', broker=broker_url)
celery.conf.update(
    worker_hijack_root_logger=False,
)


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


@celery.task(name='convert_audio')
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
    db.update_task(task, status=TaskStatus.audio_converting)
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
    logger.info('Publishing transcribe audio task for task_id: %s', task.id)
    transcribe_audio.delay(task.id)
    logger.info('Removing temporary file id: %s', temp_file_id)
    db.remove_temp_file(temp_file_id)
    logger.info('Audio converted successfully.')
