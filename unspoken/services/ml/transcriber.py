import logging
from io import BytesIO

import torch
from faster_whisper import WhisperModel

from unspoken.settings import settings
from unspoken.enitites.speach_to_text import SpeachToTextResult, SpeachToTextSegment
from unspoken.enitites.enums.ml_models import Model

logger = logging.getLogger(__name__)


class Transcriber:
    def __init__(self):
        self._model = WhisperModel(
            model_size_or_path=Model.large_v3.path(),
            device=settings.device,
            device_index=settings.device_index,
            compute_type=settings.compute_type,
            download_root=settings.models_dir_path,
        )

    def transcribe(self, audio: bytes) -> SpeachToTextResult:
        with torch.no_grad():
            segments, info = self._model.transcribe(
                BytesIO(audio),
                language='ru',
                task='transcribe',
            )
        result = SpeachToTextResult()
        for segment in segments:
            result.segments.append(
                SpeachToTextSegment(
                    id=segment.id,
                    start=segment.start,
                    end=segment.end,
                    text=segment.text.strip(),
                )
            )
        return result
