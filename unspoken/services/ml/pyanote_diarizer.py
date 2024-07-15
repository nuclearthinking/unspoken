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
        with NamedTemporaryFile(suffix='.wav') as fp:
            fp.write(wav_data)
            fp.flush()
            with torch.no_grad():
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
        return result
