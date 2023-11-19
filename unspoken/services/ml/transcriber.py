from io import BytesIO

import torch
from faster_whisper import WhisperModel

from unspoken.enitites.speach_to_text import SpeachToTextResult, SpeachToTextSegment
from unspoken.settings import settings


class Transcriber:
    def __init__(self):
        self._model = WhisperModel(
            model_size_or_path='large-v2',
            device=settings.device,
            compute_type=settings.compute_type,
            download_root='models',
        )

    def transcribe(self, audio: bytes) -> SpeachToTextResult:
        segments, info = self._model.transcribe(BytesIO(audio), language='ru', vad_filter=False)
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
        del self._model
        torch.cuda.empty_cache()
        return result


class TranscriberFactory:
    __transcriber = None

    @staticmethod
    def get_transcriber() -> Transcriber:
        if TranscriberFactory.__transcriber is None:
            TranscriberFactory.__transcriber = Transcriber()
        return TranscriberFactory.__transcriber
