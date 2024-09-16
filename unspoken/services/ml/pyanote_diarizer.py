import time
import logging
from pathlib import Path
from tempfile import NamedTemporaryFile

import torch
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.speaker_diarization import SpeakerDiarization

from unspoken.core.device import get_device
from unspoken.enitites.diarization import SpeakerSegment, DiarizationResult
from unspoken.enitites.enums.ml_models import Model
from unspoken.services.ml.base_diarizer import BaseDiarizer

logger = logging.getLogger(__name__)


class _Pipeline(Pipeline):
    @classmethod
    def from_pretrained(cls, model_path) -> 'Pipeline':  # noqa
        path_segmentation_model = str(Path(model_path) / 'segmentation_checkpoint.bin')
        path_embedding_model = str(Path(model_path) / 'embedding_checkpoint.bin')

        pipeline = SpeakerDiarization(
            segmentation_batch_size=32,
            embedding_batch_size=32,
            embedding_exclude_overlap=True,
            segmentation=path_segmentation_model,
            embedding=path_embedding_model,
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
        self._pipeline = _Pipeline.from_pretrained(
            Model.diarization.path(),
        ).to(get_device())

    @torch.inference_mode()
    def diarize(self, wav_data: bytes) -> DiarizationResult:
        start_time = time.time()
        with NamedTemporaryFile(suffix='.wav') as fp:
            fp.write(wav_data)
            fp.flush()
            diarization = self._pipeline(fp.name)

        result = DiarizationResult()
        speakers = set()
        for id_, (segment, _, speaker) in enumerate(diarization.itertracks(yield_label=True)):
            speakers.add(speaker.lower())
            result.segments.append(
                SpeakerSegment(
                    id=id_,
                    start=float(round(segment.start, 3)),
                    end=float(round(segment.end, 3)),
                    speaker=speaker.lower(),
                    duration=float(round(segment.duration, 3)),
                )
            )
        result.speakers = list(speakers)
        end_time = time.time()
        diarization_time = end_time - start_time
        logger.info(f'Diarization completed in {diarization_time:.3f} seconds.')
        return result
