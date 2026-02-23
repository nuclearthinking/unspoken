import logging
import time
from pathlib import Path
from tempfile import NamedTemporaryFile

import torch
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.speaker_diarization import SpeakerDiarization

from unspoken.core.device import get_device
from unspoken.enitites.diarization import DiarizationResult, SpeakerSegment
from unspoken.enitites.enums.ml_models import Model
from unspoken.services.ml.base_diarizer import BaseDiarizer

logger = logging.getLogger(__name__)


def _build_pipeline(model_path: str) -> SpeakerDiarization:
    path_segmentation_model = str(Path(model_path) / 'segmentation_checkpoint.bin')
    path_embedding_model = str(Path(model_path) / 'embedding_checkpoint.bin')

    pipeline = SpeakerDiarization(
        segmentation=path_segmentation_model,
        embedding=path_embedding_model,
        embedding_exclude_overlap=True,
        clustering='AgglomerativeClustering',
        segmentation_batch_size=32,
        embedding_batch_size=32,
    )

    pipeline.instantiate(
        {
            'clustering': {
                'method': 'centroid',
                'min_cluster_size': 12,
                'threshold': 0.7045654963945799,
            },
            'segmentation': {
                'min_duration_off': 0.5,
            },
        }
    )
    return pipeline


class PyanoteDiarizer(BaseDiarizer):
    def __init__(self):
        super().__init__()
        init_started_at = time.perf_counter()
        logger.info('Diarization pipeline initialization started from %s.', Model.diarization.path())
        self._pipeline = _build_pipeline(Model.diarization.path()).to(get_device())
        init_elapsed = time.perf_counter() - init_started_at
        logger.info('Diarization pipeline initialization finished in %.2fs.', init_elapsed)

    @torch.inference_mode()
    def diarize(self, wav_data: bytes) -> DiarizationResult:
        start_time = time.time()
        with NamedTemporaryFile(suffix='.wav') as fp:
            fp.write(wav_data)
            fp.flush()
            diarization = self._pipeline(fp.name)

        # Collect raw segments from pyannote.
        raw_segments: list[tuple[float, float, str]] = []
        for segment, _, speaker in diarization.itertracks(yield_label=True):
            raw_segments.append((
                float(round(segment.start, 3)),
                float(round(segment.end, 3)),
                speaker.lower(),
            ))

        # Merge adjacent segments from the same speaker when the gap
        # between them is negligible (< 0.15s).  This reduces over-
        # fragmentation that confuses the alignment step.
        merged = _merge_adjacent_segments(raw_segments, max_gap=0.15)

        result = DiarizationResult()
        speakers = set()
        for id_, (seg_start, seg_end, speaker) in enumerate(merged):
            speakers.add(speaker)
            result.segments.append(
                SpeakerSegment(
                    id=id_,
                    start=seg_start,
                    end=seg_end,
                    speaker=speaker,
                    duration=float(round(seg_end - seg_start, 3)),
                )
            )
        result.speakers = list(speakers)
        result.speakers_count = len(speakers)
        end_time = time.time()
        diarization_time = end_time - start_time
        logger.info(
            'Diarization completed in %.3f seconds (%d raw -> %d merged segments).',
            diarization_time, len(raw_segments), len(merged),
        )
        return result


def _merge_adjacent_segments(
    segments: list[tuple[float, float, str]],
    max_gap: float = 0.15,
) -> list[tuple[float, float, str]]:
    """Merge consecutive segments from the same speaker when the silence
    gap between them is at most *max_gap* seconds."""

    if not segments:
        return []

    merged: list[tuple[float, float, str]] = [segments[0]]
    for start, end, speaker in segments[1:]:
        prev_start, prev_end, prev_speaker = merged[-1]
        if speaker == prev_speaker and (start - prev_end) <= max_gap:
            merged[-1] = (prev_start, end, speaker)
        else:
            merged.append((start, end, speaker))
    return merged
