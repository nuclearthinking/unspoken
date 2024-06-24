from tempfile import NamedTemporaryFile

import torch
from pyannote.audio import Pipeline

from unspoken.settings import settings
from unspoken.enitites.diarization import SpeakerSegment, DiarizationResult
from unspoken.services.ml.base_diarizer import BaseDiarizer


class PyanoteDiarizer(BaseDiarizer):
    def __init__(self):
        super().__init__()
        self._pipeline = Pipeline.from_pretrained(
            'pyannote/speaker-diarization-3.1',
            use_auth_token=settings.hf_token,
        ).to(torch.device(f'{settings.device}:{settings.device_index}'))

    def diarize(self, wav_data: bytes) -> DiarizationResult:
        with NamedTemporaryFile(suffix='.rttm') as fp:
            fp.write(wav_data)
            fp.flush()
            diarization = self._pipeline(fp.name)
        result = DiarizationResult()

        for id_, (segment, _, speaker) in enumerate(diarization.itertracks(yield_label=True)):
            result.segments.append(
                SpeakerSegment(
                    id=id_,
                    start=float(segment.start),
                    end=float(segment.end),
                    speaker=speaker,
                    duration=float(segment.duration),
                )
            )
        return result
