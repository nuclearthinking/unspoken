import logging
from collections import defaultdict
from operator import itemgetter

from unspoken.enitites.diarization import DiarizationResult, SpeakerSegment
from unspoken.enitites.speach_to_text import SpeachToTextResult
from unspoken.enitites.transcription import TranscriptionResult, TranscriptionSegment
import numpy as np
from typing import List, Tuple

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
    total_duration = end - start
    for segment in segments:
        # Calculate overlap between transcription segment and speaker segment
        overlap_start = max(start, segment.start)
        overlap_end = min(end, segment.end)
        if overlap_start < overlap_end:  # There is an overlap
            overlap_duration = overlap_end - overlap_start
            speaker_counter[segment.speaker] += overlap_duration / total_duration

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

    # Sort diarization segments by start time for efficient searching
    sorted_diarization_segments = sorted(diarization_segments, key=lambda x: x.start)

    for segment in stt_segments:
        # Find relevant diarization segments for this STT segment
        relevant_segments = [
            s for s in sorted_diarization_segments
            if s.start < segment.end and s.end > segment.start
        ]
        
        speaker = _determine_speaker_by_time(start=segment.start, end=segment.end, segments=relevant_segments)
        
        result.messages.append(
            TranscriptionSegment(
                speaker=speaker,
                start=segment.start,
                end=segment.end,
                text=segment.text,
            )
        )
    return result





def dtw(seq1: List[Tuple[float, float]], seq2: List[Tuple[float, float]]) -> List[Tuple[int, int]]:
    """
    Perform Dynamic Time Warping on two sequences of time intervals.
    
    :param seq1: List of (start, end) tuples for the first sequence (e.g., transcription)
    :param seq2: List of (start, end) tuples for the second sequence (e.g., diarization)
    :return: List of matched indices (i, j) where i is the index in seq1 and j is the index in seq2
    """
    n, m = len(seq1), len(seq2)
    dtw_matrix = np.zeros((n+1, m+1))
    dtw_matrix[0, 1:] = np.inf
    dtw_matrix[1:, 0] = np.inf
    
    for i in range(1, n+1):
        for j in range(1, m+1):
            cost = abs(seq1[i-1][0] - seq2[j-1][0]) + abs(seq1[i-1][1] - seq2[j-1][1])
            dtw_matrix[i, j] = cost + min(dtw_matrix[i-1, j], dtw_matrix[i, j-1], dtw_matrix[i-1, j-1])
    
    # Backtracking to find the optimal path
    i, j = n, m
    path = [(i-1, j-1)]
    while i > 1 and j > 1:
        if i == 1:
            j -= 1
        elif j == 1:
            i -= 1
        else:
            if dtw_matrix[i-1, j-1] == min(dtw_matrix[i-1, j-1], dtw_matrix[i-1, j], dtw_matrix[i, j-1]):
                i, j = i-1, j-1
            elif dtw_matrix[i-1, j] == min(dtw_matrix[i-1, j-1], dtw_matrix[i-1, j], dtw_matrix[i, j-1]):
                i -= 1
            else:
                j -= 1
        path.append((i-1, j-1))
    
    return path[::-1]

def align_transcription_and_diarization(transcription: List[TranscriptionSegment], 
                                        diarization: List[SpeakerSegment]) -> List[TranscriptionSegment]:
    """
    Align transcription segments with diarization segments using DTW.
    
    :param transcription: List of TranscriptionSegment objects
    :param diarization: List of SpeakerSegment objects
    :return: List of aligned TranscriptionSegment objects with updated speaker information
    """
    trans_intervals = [(seg.start, seg.end) for seg in transcription]
    diar_intervals = [(seg.start, seg.end) for seg in diarization]
    
    alignment = dtw(trans_intervals, diar_intervals)
    
    aligned_transcription = []
    for trans_idx, diar_idx in alignment:
        aligned_segment = TranscriptionSegment(
            speaker=diarization[diar_idx].speaker,
            start=transcription[trans_idx].start,
            end=transcription[trans_idx].end,
            text=transcription[trans_idx].text
        )
        aligned_transcription.append(aligned_segment)
    
    return aligned_transcription

# Usage in your annotate function:
def annotate_dtw(stt_result: SpeachToTextResult, diarization_result: DiarizationResult) -> TranscriptionResult:
    result = TranscriptionResult()
    aligned_segments = align_transcription_and_diarization(stt_result.segments, diarization_result.segments)
    result.messages = aligned_segments
    return result