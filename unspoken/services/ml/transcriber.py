import logging
import time
from io import BytesIO

import torch
from faster_whisper import WhisperModel

from unspoken.core.singleton import SingletonMeta
from unspoken.enitites.enums.ml_models import Model
from unspoken.enitites.speach_to_text import SpeachToTextResult, SpeachToTextSegment
from unspoken.settings import settings

logger = logging.getLogger(__name__)


class Transcriber(metaclass=SingletonMeta):
    def __init__(self):
        init_started_at = time.perf_counter()
        logger.info('Whisper initialization started from %s.', Model.large_v3.path())
        self._model = WhisperModel(
            model_size_or_path=Model.large_v3.path(),
            device=settings.device,
            device_index=settings.device_index,
            compute_type=settings.compute_type,
            download_root=settings.models_dir_path,
        )
        init_elapsed = time.perf_counter() - init_started_at
        logger.info('Whisper initialization finished in %.2fs.', init_elapsed)

    @torch.inference_mode()
    def transcribe(self, audio: bytes) -> SpeachToTextResult:
        start_time = time.time()
        segments, info = self._model.transcribe(
            BytesIO(audio),
            language='ru',
            task='transcribe',
            word_timestamps=True,
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
        end_time = time.time()
        transcription_time = end_time - start_time
        logger.info('Transcription completed in %.3f seconds.', transcription_time)
        torch.cuda.empty_cache()
        return result
