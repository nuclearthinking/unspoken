import logging

import torch

from unspoken import exceptions
from unspoken.services import db
from unspoken.enitites.diarization import DiarizationResult
from unspoken.enitites.transcription import TranscriptionResult
from unspoken.enitites.speach_to_text import SpeachToTextResult
from unspoken.services.ml.transcriber import Transcriber
from unspoken.services.audio.converter import convert_to_wav
from unspoken.enitites.enums.task_status import TaskStatus
from unspoken.services.ml.pyanote_diarizer import PyanoteDiarizer
from unspoken.services.annotation.annotate_transcription import annotate

logger = logging.getLogger(__name__)


def _convert_audio(source_file_data: bytes):
    wav_data = convert_to_wav(source_file_data)
    return wav_data


def _transcribe_audio(wav_data: bytes) -> SpeachToTextResult:
    torch.cuda.empty_cache()
    result = Transcriber().transcribe(wav_data)
    torch.cuda.synchronize()
    return result


def _diarize_audio(wav_data: bytes) -> DiarizationResult:
    torch.cuda.empty_cache()
    result = PyanoteDiarizer().diarize(wav_data)
    torch.cuda.synchronize()
    return result


def _combine_results(stt_result: SpeachToTextResult, diarization_result: DiarizationResult) -> TranscriptionResult:
    return annotate(stt_result, diarization_result)


def _save_to_database(transcription: TranscriptionResult, task_id: int) -> None:
    db.save_transcription_result(
        task_id,
        transcription.dict(),
    )


def transcribe_audio_flow(temp_file_id: int, task_id: int):
    logger.info('Starting transcription flow for task %s.', task_id)
    temp_file = db.get_temp_file(temp_file_id)
    if not temp_file:
        logger.error('Not found temporary file with id: %s.', temp_file_id)
        raise exceptions.TempFileNotFoundError(f'Temp file with id {temp_file_id} not found.')

    task = db.get_task(task_id)
    if not task:
        logger.error('Task with id: %s was not found.', task_id)
        temp_file.delete()
        raise exceptions.TaskNotFoundError(f'Task with id: {task_id} was not found.')
    try:
        db.update_task(task, status=TaskStatus.transcribing)
        logger.info('Converting audio for tmp_file_id %s.', temp_file_id)
        wav_data = _convert_audio(source_file_data=temp_file.read())
        logger.info('Diarizing audio for task_id %s.', task_id)
        diarization = _diarize_audio(wav_data)
        logger.info('Transcribing audio for task_id %s.', task_id)
        transcription = _transcribe_audio(wav_data)
        logger.info('Combining results for task_id %s.', task_id)
        combined = _combine_results(stt_result=transcription, diarization_result=diarization)
        logger.info('Saving results for task_id %s.', task_id)
        _save_to_database(combined, task_id)
        db.update_task(task, status=TaskStatus.completed)
        logger.info('Transcription flow completed for task %s.', task_id)
    except Exception:
        logger.exception('Exception occurred during running transcription flow.')
        db.update_task(task, status=TaskStatus.failed)
        raise
    finally:
        temp_file.delete()
