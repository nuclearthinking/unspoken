import logging
from operator import itemgetter
from collections import defaultdict

from unspoken.services import db
from unspoken.settings import settings
from unspoken.enitites.diarization import SpeakerSegment, DiarizationResult
from unspoken.services.queue.broker import celery
from unspoken.enitites.transcription import TranscriptionResult, TranscriptionSegment
from unspoken.enitites.speach_to_text import SpeachToTextResult
from unspoken.enitites.enums.task_status import TaskStatus

logger = logging.getLogger(__name__)


@celery.task(
    name='complete_transcription',
    queue=settings.low_resource_demand_queue,
    routing_key='low.complete_transcription',
)
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
    logger.info('Combining speach to text and diarization results for task %s', task.id)
    transcription = _combine_results(
        speach_to_text_result=SpeachToTextResult.parse_obj(task.transcript.speach_to_text_result),
        diarization_result=DiarizationResult.parse_obj(task.transcript.diarization_result),
    )
    db.save_transcription_result(task.id, transcription.dict())
    db.update_task(task, status=TaskStatus.completed)
    logger.info('Transcription completed for task %s', task.id)


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
        speaker = get_who_speaking(start=segment.start, end=segment.end, segments=diarization_segments)
        result.messages.append(
            TranscriptionSegment(
                speaker=speaker,
                start=segment.start,
                end=segment.end,
                text=segment.text,
            )
        )
    return result


def get_who_speaking(start: float, end: float, segments: list[SpeakerSegment]) -> str:
    speaker_counter = defaultdict(float)
    hit_segments = []
    for segment in segments:
        if start <= segment.start <= end and start <= segment.end or segment.start <= start <= segment.end:
            hit_segments.append(segment)
            speaker_counter[segment.speaker] += segment.end - start
    if not speaker_counter:
        logger.info('No speaker speaking')
        return 'unknown'
    logger.info('Speaker counter now %s', speaker_counter)
    logger.info('Hit segments %s', hit_segments)
    speaker = next(iter(sorted(speaker_counter.items(), key=itemgetter(1), reverse=True)), None)
    speaker = speaker[0]
    logger.info('Speaker %s speaking', speaker)
    return speaker
