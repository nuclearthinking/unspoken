from io import BytesIO

from faster_whisper import WhisperModel

from unspoken.settings import settings


class Transcriber:
    def __init__(self):
        self._model = WhisperModel(
            model_size_or_path='large-v2',
            device=settings.device,
            compute_type=settings.compute_type,
            download_root='models',
        )

    def transcribe(self, audio: bytes) -> str:
        segments, info = self._model.transcribe(BytesIO(audio), language='ru')
        result = []
        for segment in segments:
            result.append(segment)
            print(segment)
        return result


class TranscriberFactory:
    __transcriber = None

    @staticmethod
    def get_transcriber() -> Transcriber:
        if TranscriberFactory.__transcriber is None:
            TranscriberFactory.__transcriber = Transcriber()
        return TranscriberFactory.__transcriber
