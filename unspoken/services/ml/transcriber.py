from faster_whisper import WhisperModel

from unspoken.settings import settings


class TranscriberFactory:
    ...


class Transcriber:

    def __init__(self):
        self._model = WhisperModel(
            model_size_or_path='large-v2',
            device=settings.device,
            compute_type=settings.compute_type,
            download_root='models',
        )

    def transcribe(self, audio: bytes) -> str:
        segments, info = self._model.transcribe(audio, language='ru')
        result = []
        for segment in segments:
            print(segment)
            result.append(segment)
        return result





transcriber = Transcriber()
transcriber.transcribe(open('sample.mp3', 'rb'))
