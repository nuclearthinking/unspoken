import io
import logging
from tempfile import NamedTemporaryFile

import librosa
import soundfile as sf
import noisereduce as nr
from pydub import AudioSegment

logger = logging.getLogger(__name__)


def _to_segment(audio_data: bytes, format_: str | None = 'wav') -> AudioSegment:
    with NamedTemporaryFile('w+b') as file:
        file.write(audio_data)
        return AudioSegment.from_file(file.name, format=format_)


def _from_segment(segment: AudioSegment, format_: str = 'wav', **kwargs) -> bytes:
    with NamedTemporaryFile('w+b') as file:
        segment.export(file.name, format=format_, **kwargs)
        return file.read()


def convert_to_wav(source_data: bytes, sample_rate: str = '44100', bit_rate: str = '16k') -> bytes:
    segment = _to_segment(source_data, format_=None)

    return _from_segment(
        segment,
        format_='wav',
        parameters=[
            '-ar',
            sample_rate,
            '-ab',
            bit_rate,
            '-ac',
            '1',
        ],
    )


def preprocess_audio(wav_data: bytes) -> bytes:
    audio_stream = io.BytesIO(wav_data)
    y, sr = librosa.load(audio_stream, sr=None)

    reduced_noise = nr.reduce_noise(y=y, sr=sr)

    normalized_audio = librosa.util.normalize(reduced_noise)

    processed_audio_stream = io.BytesIO()
    sf.write(processed_audio_stream, normalized_audio, sr, format='WAV')
    processed_audio_bytes = processed_audio_stream.getvalue()

    return processed_audio_bytes
