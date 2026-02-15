import bisect
import logging
from collections import defaultdict
from typing import List, Tuple

import numpy as np

from unspoken.enitites.diarization import DiarizationResult, SpeakerSegment
from unspoken.enitites.speach_to_text import SpeachToTextResult, SpeachToTextSegment
from unspoken.enitites.transcription import TranscriptionResult, TranscriptionSegment

logger = logging.getLogger(__name__)
UNKNOWN_SPEAKER = 'unknown'
MIN_OVERLAP_RATIO = 0.2
MAX_BOUNDARY_COST_SECONDS = 0.75
NEAREST_NEIGHBOR_TOLERANCE_SECONDS = 2.0


def _is_positive_duration(start: float, end: float) -> bool:
    return end > start


def _overlap_duration(
    start_a: float,
    end_a: float,
    start_b: float,
    end_b: float,
) -> float:
    return max(0.0, min(end_a, end_b) - max(start_a, start_b))


# ---------------------------------------------------------------------------
# Overlap-based speaker assignment (primary strategy)
# ---------------------------------------------------------------------------

def _assign_speakers_by_overlap(
    transcription: List[SpeachToTextSegment],
    diarization: List[SpeakerSegment],
) -> List[str]:
    """For each STT segment, find overlapping diarization segments and vote
    by total overlap duration.  Returns a list of speaker labels (or
    ``UNKNOWN_SPEAKER``) aligned with *transcription*."""

    speakers: List[str] = [UNKNOWN_SPEAKER] * len(transcription)
    if not diarization:
        return speakers

    # Sort diarization segments by start time for efficient search.
    sorted_diar = sorted(diarization, key=lambda s: s.start)
    diar_starts = [s.start for s in sorted_diar]

    for idx, seg in enumerate(transcription):
        if not _is_positive_duration(seg.start, seg.end):
            continue

        # Binary search: find diarization segments that *could* overlap
        # with [seg.start, seg.end].
        # A diarization segment overlaps if diar.start < seg.end AND diar.end > seg.start.
        # We look for segments whose start < seg.end (right bound) starting from
        # the first one whose end could be > seg.start.
        right = bisect.bisect_left(diar_starts, seg.end)

        overlap_by_speaker: dict[str, float] = defaultdict(float)
        # Walk backwards from `right` while diar segment end > seg.start.
        for i in range(right - 1, -1, -1):
            d = sorted_diar[i]
            if d.end <= seg.start:
                break
            overlap = _overlap_duration(seg.start, seg.end, d.start, d.end)
            if overlap > 0:
                overlap_by_speaker[d.speaker] += overlap

        if overlap_by_speaker:
            speakers[idx] = max(overlap_by_speaker, key=overlap_by_speaker.get)  # type: ignore[arg-type]

    return speakers


# ---------------------------------------------------------------------------
# Nearest-neighbor fallback for segments with no overlap
# ---------------------------------------------------------------------------

def _fill_nearest_neighbor(
    transcription: List[SpeachToTextSegment],
    diarization: List[SpeakerSegment],
    speakers: List[str],
    tolerance: float = NEAREST_NEIGHBOR_TOLERANCE_SECONDS,
) -> None:
    """For still-unknown segments, assign the speaker of the nearest
    diarization segment within *tolerance* seconds.  Modifies *speakers*
    in place."""

    if not diarization:
        return

    sorted_diar = sorted(diarization, key=lambda s: s.start)
    diar_starts = [s.start for s in sorted_diar]

    for idx, seg in enumerate(transcription):
        if speakers[idx] != UNKNOWN_SPEAKER:
            continue
        if not _is_positive_duration(seg.start, seg.end):
            continue

        seg_mid = (seg.start + seg.end) / 2.0
        pos = bisect.bisect_left(diar_starts, seg_mid)

        best_speaker = UNKNOWN_SPEAKER
        best_dist = tolerance

        # Check the segment at `pos` and `pos - 1` (closest by midpoint).
        for candidate_idx in (pos - 1, pos):
            if 0 <= candidate_idx < len(sorted_diar):
                d = sorted_diar[candidate_idx]
                # Distance = gap between the two intervals (0 if they touch).
                dist = max(0.0, seg.start - d.end, d.start - seg.end)
                if dist < best_dist:
                    best_dist = dist
                    best_speaker = d.speaker

        speakers[idx] = best_speaker


# ---------------------------------------------------------------------------
# Context propagation: inherit speaker from neighbours for remaining unknowns
# ---------------------------------------------------------------------------

def _propagate_from_neighbors(
    speakers: List[str],
) -> None:
    """Fill remaining unknowns by copying the speaker label of the closest
    known neighbour (prefer previous, then next).  Modifies *speakers*
    in place."""

    n = len(speakers)
    if n == 0:
        return

    # Forward pass: propagate from left.
    last_known = UNKNOWN_SPEAKER
    for i in range(n):
        if speakers[i] != UNKNOWN_SPEAKER:
            last_known = speakers[i]
        elif last_known != UNKNOWN_SPEAKER:
            speakers[i] = last_known

    # Backward pass: fill any leading unknowns from the right.
    last_known = UNKNOWN_SPEAKER
    for i in range(n - 1, -1, -1):
        if speakers[i] != UNKNOWN_SPEAKER:
            last_known = speakers[i]
        elif last_known != UNKNOWN_SPEAKER:
            speakers[i] = last_known


# ---------------------------------------------------------------------------
# Public entry-point: overlap → nearest-neighbour → context propagation
# ---------------------------------------------------------------------------

def align_transcription_and_diarization(
    transcription: List[SpeachToTextSegment], diarization: List[SpeakerSegment]
) -> List[TranscriptionSegment]:
    """Align transcription segments with diarization using overlap-based
    speaker voting, nearest-neighbour fallback and context propagation."""

    if not transcription:
        return []
    if not diarization:
        return [
            TranscriptionSegment(speaker=UNKNOWN_SPEAKER, start=seg.start, end=seg.end, text=seg.text)
            for seg in transcription
        ]

    valid_diarization = [
        seg for seg in diarization if _is_positive_duration(seg.start, seg.end)
    ]

    # 1. Primary: overlap-based vote.
    speakers = _assign_speakers_by_overlap(transcription, valid_diarization)

    unknown_after_overlap = sum(1 for s in speakers if s == UNKNOWN_SPEAKER)
    if unknown_after_overlap:
        logger.debug(
            'Overlap pass left %d / %d segments unknown.',
            unknown_after_overlap,
            len(transcription),
        )

    # 2. Fallback: nearest diarization segment within tolerance.
    _fill_nearest_neighbor(transcription, valid_diarization, speakers)

    unknown_after_nn = sum(1 for s in speakers if s == UNKNOWN_SPEAKER)
    if unknown_after_nn:
        logger.debug(
            'Nearest-neighbour pass left %d / %d segments unknown.',
            unknown_after_nn,
            len(transcription),
        )

    # 3. Last resort: inherit from adjacent assigned segments.
    _propagate_from_neighbors(speakers)

    unknown_final = sum(1 for s in speakers if s == UNKNOWN_SPEAKER)
    if unknown_final:
        logger.warning(
            '%d / %d segments remain unknown after all assignment passes.',
            unknown_final,
            len(transcription),
        )

    return [
        TranscriptionSegment(speaker=spk, start=seg.start, end=seg.end, text=seg.text)
        for seg, spk in zip(transcription, speakers)
    ]


# ---------------------------------------------------------------------------
# Legacy DTW alignment (kept for reference / fallback)
# ---------------------------------------------------------------------------

def _is_acceptable_match(
    transcription_segment: SpeachToTextSegment,
    diarization_segment: SpeakerSegment,
    boundary_cost: float,
) -> bool:
    trans_duration = transcription_segment.end - transcription_segment.start
    if trans_duration <= 0:
        return False

    overlap = _overlap_duration(
        transcription_segment.start,
        transcription_segment.end,
        diarization_segment.start,
        diarization_segment.end,
    )
    overlap_ratio = overlap / trans_duration
    if overlap_ratio >= MIN_OVERLAP_RATIO:
        return True
    return boundary_cost <= MAX_BOUNDARY_COST_SECONDS


def dtw(seq1: List[Tuple[float, float]], seq2: List[Tuple[float, float]]) -> List[Tuple[int, int]]:
    """Perform Dynamic Time Warping on two interval sequences."""
    n, m = len(seq1), len(seq2)
    dtw_matrix = np.zeros((n + 1, m + 1))
    dtw_matrix[0, 1:] = np.inf
    dtw_matrix[1:, 0] = np.inf

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = abs(seq1[i - 1][0] - seq2[j - 1][0]) + abs(seq1[i - 1][1] - seq2[j - 1][1])
            dtw_matrix[i, j] = cost + min(dtw_matrix[i - 1, j], dtw_matrix[i, j - 1], dtw_matrix[i - 1, j - 1])

    i, j = n, m
    path = [(i - 1, j - 1)]
    while i > 1 or j > 1:
        if i == 1:
            j -= 1
        elif j == 1:
            i -= 1
        else:
            if dtw_matrix[i - 1, j - 1] <= dtw_matrix[i - 1, j] and dtw_matrix[i - 1, j - 1] <= dtw_matrix[i, j - 1]:
                i, j = i - 1, j - 1
            elif dtw_matrix[i - 1, j] <= dtw_matrix[i, j - 1]:
                i -= 1
            else:
                j -= 1
        path.append((i - 1, j - 1))

    return path[::-1]


def annotate_dtw(stt_result: SpeachToTextResult, diarization_result: DiarizationResult) -> TranscriptionResult:
    result = TranscriptionResult()
    if not stt_result.segments:
        return result
    invalid_stt_segments = sum(
        1 for segment in stt_result.segments if not _is_positive_duration(segment.start, segment.end)
    )
    if invalid_stt_segments:
        logger.warning(
            'Detected %s STT segments with non-positive duration. They will be returned as unknown.',
            invalid_stt_segments,
        )

    aligned_segments = align_transcription_and_diarization(stt_result.segments, diarization_result.segments)
    result.messages = aligned_segments
    return result
