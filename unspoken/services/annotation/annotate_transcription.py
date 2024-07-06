import logging
from operator import itemgetter
from collections import defaultdict

from unspoken.enitites.diarization import SpeakerSegment, DiarizationResult
from unspoken.enitites.transcription import TranscriptionResult, TranscriptionSegment
from unspoken.enitites.speach_to_text import SpeachToTextResult

logger = logging.getLogger(__name__)


def _get_who_speaking(start: float, end: float, segments: list[SpeakerSegment]) -> str:
    speaker_counter = defaultdict(float)
    hit_segments = []
    for segment in segments:
        if start <= segment.start <= end and start <= segment.end or segment.start <= start <= segment.end:
            hit_segments.append(segment)
            speaker_counter[segment.speaker] += segment.end - start
    if not speaker_counter:
        logger.info('No speaker speaking')
        return 'unknown'
    logger.debug('Speaker counter now %s', speaker_counter)
    logger.debug('Hit segments %s', hit_segments)
    speaker = next(iter(sorted(speaker_counter.items(), key=itemgetter(1), reverse=True)), None)
    speaker = speaker[0]
    logger.debug('Speaker %s speaking', speaker)
    return speaker


def annotate(stt_result: SpeachToTextResult, diarization_result: DiarizationResult) -> TranscriptionResult:
    result = TranscriptionResult()
    stt_segments = stt_result.segments
    diarization_segments = diarization_result.segments
    for segment in stt_segments:
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
