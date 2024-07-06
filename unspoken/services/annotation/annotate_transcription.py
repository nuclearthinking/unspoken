import logging
from operator import itemgetter
from collections import defaultdict

from unspoken.enitites.diarization import SpeakerSegment, DiarizationResult
from unspoken.enitites.transcription import TranscriptionResult, TranscriptionSegment
from unspoken.enitites.speach_to_text import SpeachToTextResult

logger = logging.getLogger(__name__)


def _determine_speaker_by_time(start: float, end: float, segments: list[SpeakerSegment]) -> str:
    """
    Determine the speaker based on the start and end timestamps and the given segments.

    :param start: The start timestamp.
    :param end: The end timestamp.
    :param segments: A list of SpeakerSegment objects.
    :return: The speaker ID or 'unknown' if no speaker is found.
    """
    speaker_counter = defaultdict(float)
    for segment in segments:
        # Calculate overlap between transcription segment and speaker segment
        overlap_start = max(start, segment.start)
        overlap_end = min(end, segment.end)
        if overlap_start < overlap_end:  # There is an overlap
            overlap_duration = overlap_end - overlap_start
            speaker_counter[segment.speaker] += overlap_duration

    if not speaker_counter:
        logger.info('No speaker speaking')
        return 'unknown'

    logger.debug('Speaker counter now %s', speaker_counter)
    speaker = max(speaker_counter.items(), key=itemgetter(1))[0]
    logger.debug('Speaker %s speaking', speaker)
    return speaker


def _determine_speaker_by_hit_count(start: float, end: float, segments: list[SpeakerSegment]) -> str:
    """
    Determine the speaker based on the start and end timestamps and the given segments.

    :param start: The start timestamp.
    :param end: The end timestamp.
    :param segments: A list of SpeakerSegment objects.
    :return: The speaker ID or 'unknown' if no speaker is found.
    """
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
    """
    Annotate the speech-to-text result with speaker information from the diarization result.

    :param stt_result: The SpeachToTextResult object containing the speech-to-text segments.
    :param diarization_result: The DiarizationResult object containing the speaker diarization segments.
    :return: A TranscriptionResult object with annotated speaker information.
    """
    result = TranscriptionResult()
    stt_segments = stt_result.segments
    diarization_segments = diarization_result.segments
    for segment in stt_segments:
        speaker = _determine_speaker_by_time(start=segment.start, end=segment.end, segments=diarization_segments)
        result.messages.append(
            TranscriptionSegment(
                speaker=speaker,
                start=segment.start,
                end=segment.end,
                text=segment.text,
            )
        )
    return result
