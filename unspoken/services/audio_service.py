import io
import logging
from tempfile import NamedTemporaryFile

import ffmpeg
import librosa
import soundfile as sf
import noisereduce as nr

logger = logging.getLogger(__name__)


def _convert_to_wav(source_data: bytes) -> bytes:
    try:
        with (
            NamedTemporaryFile(delete=False, suffix='.tmp') as temp_input,
            NamedTemporaryFile(delete=False, suffix='.wav') as temp_output,
        ):
            temp_input.write(source_data)
            temp_input_path = temp_input.name
            temp_output_path = temp_output.name

            (
                ffmpeg.input(temp_input_path)
                .filter('loudnorm')
                .output(temp_output_path, format='wav', acodec='pcm_s16le', ar=16000, ac=1)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )

            with open(temp_output_path, 'rb') as output_file:
                out = output_file.read()

            return out

    except ffmpeg.Error as e:
        logger.error(f'FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}')
        raise


def _convert_wav_to_mp3(wav_data: bytes, bitrate: str = '128k') -> bytes:
    try:
        with (
            NamedTemporaryFile(delete=False, suffix='.wav') as temp_input,
            NamedTemporaryFile(delete=False, suffix='.mp3') as temp_output,
        ):
            temp_input.write(wav_data)
            temp_input_path = temp_input.name
            temp_output_path = temp_output.name

            (
                ffmpeg.input(temp_input_path)
                .output(temp_output_path, format='mp3', acodec='libmp3lame', audio_bitrate=bitrate)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )

            with open(temp_output_path, 'rb') as output_file:
                out = output_file.read()

            return out

    except ffmpeg.Error as e:
        logger.error(f'FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}')
        raise


def preprocess_audio(wav_data: bytes) -> bytes:
    audio_stream = io.BytesIO(wav_data)
    y, sr = librosa.load(audio_stream, sr=None)

    reduced_noise = nr.reduce_noise(y=y, sr=sr)

    normalized_audio = librosa.util.normalize(reduced_noise)

    processed_audio_stream = io.BytesIO()
    sf.write(processed_audio_stream, normalized_audio, sr, format='WAV')
    processed_audio_bytes = processed_audio_stream.getvalue()

    return processed_audio_bytes


class AudioService:
    def __init__(self, audio_data: bytes):
        self.audio_data = audio_data

    def to_wav(self) -> bytes:
        return _convert_to_wav(self.audio_data)

    def to_mp3(self) -> bytes:
        return _convert_wav_to_mp3(self.audio_data)

    @classmethod
    def preprocess_audio(cls, wav_data: bytes) -> bytes:
        audio_stream = io.BytesIO(wav_data)
        y, sr = librosa.load(audio_stream, sr=None)

        reduced_noise = nr.reduce_noise(y=y, sr=sr)

        normalized_audio = librosa.util.normalize(reduced_noise)

        processed_audio_stream = io.BytesIO()
        sf.write(processed_audio_stream, normalized_audio, sr, format='WAV')
        processed_audio_bytes = processed_audio_stream.getvalue()

        return processed_audio_bytes

    @classmethod
    def trim_mp3(cls, mp3_data, start: float, end: float) -> bytes:
        try:
            input_stream = ffmpeg.input('pipe:0', format='mp3')
            output_stream = (
                input_stream.filter('atrim', start=start, end=end)
                .output('pipe:1', format='mp3', acodec='libmp3lame')
                .overwrite_output()
            )

            out, _ = output_stream.run(input=mp3_data, capture_stdout=True, capture_stderr=True)
            return out
        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else 'Unknown error'
            print(f'FFmpeg error: {error_message}')
            if 'Invalid argument' in error_message or 'Error selecting filters' in error_message:
                raise ValueError(f'Invalid start or end time: {error_message}')
            raise


with open('data/interview.mp4', 'rb') as f:
    file = f.read()

wav_data = _convert_to_wav(source_data=file)

with open('result.wav', 'wb') as wf:
    wf.write(wav_data)
