import logging
from tempfile import NamedTemporaryFile

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


def convert_to_wav(file: bytes, sample_rate: str = '44100', bit_rate: str = '16k') -> bytes:
    segment = _to_segment(file, format_=None)

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
