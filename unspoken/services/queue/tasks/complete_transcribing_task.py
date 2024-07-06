import logging
import datetime

from unspoken.services import db
from unspoken.settings import settings
from unspoken.enitites.diarization import DiarizationResult
from unspoken.services.queue.broker import celery
from unspoken.enitites.transcription import TranscriptionResult, TranscriptionSegment
from unspoken.enitites.speach_to_text import SpeachToTextResult
from unspoken.enitites.enums.task_status import TaskStatus
from unspoken.services.annotation.annotate_transcription import _get_who_speaking

logger = logging.getLogger(__name__)


def complete_transcription(task_id: int) -> None:
    task = db.get_task(task_id)
    if not task:
        logger.error(f'Task {task_id} not found.')
        return
    if not all(
        [
            task.transcript.speach_to_text_result,
            task.transcript.diarization_result,
        ]
    ):
        logger.warning('Task %s is not ready to be processed.', task.id)
        return
    try:
        logger.info('Combining speach to text and diarization results for task %s', task.id)
        transcription = _combine_results(
            speach_to_text_result=SpeachToTextResult.parse_obj(task.transcript.speach_to_text_result),
            diarization_result=DiarizationResult.parse_obj(task.transcript.diarization_result),
        )
        db.save_transcription_result(task.id, transcription.dict())
        db.update_task(task, status=TaskStatus.completed, updated_at=datetime.datetime.utcnow())
        logger.info('Transcription completed for task %s', task.id)
    except Exception:
        logger.exception('Exception occurred while processing task %s', task.id)
        db.update_task(task, status=TaskStatus.failed)
    finally:
        if task.wav_file:
            task.wav_file.delete()


def _combine_results(
    speach_to_text_result: SpeachToTextResult,
    diarization_result: DiarizationResult,
) -> TranscriptionResult:
    result = TranscriptionResult()
    stt_segments = speach_to_text_result.segments
    diarization_segments = diarization_result.segments
    logger.info('STT segments %s', stt_segments)
    logger.info('Diarization segments %s', diarization_segments)
    for segment in stt_segments:
        logger.info('Processing segment %s', segment)
        speaker = _get_who_speaking(start=segment.start, end=segment.end, segments=diarization_segments)
        result.messages.append(
            TranscriptionSegment(
                speaker=speaker,
                start=segment.start,
                end=segment.end,
                text=segment.text,
            )
        )
    return result
