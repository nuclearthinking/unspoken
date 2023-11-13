import logging
import os
import pathlib
import subprocess
from tempfile import NamedTemporaryFile

from unspoken.exceptions import EncodingError

logger = logging.getLogger(__name__)

from pydub import AudioSegment


def convert_to_mp3(file: bytes) -> bytes:
    """
    The ffmpeg command arguments used:

        -i specifies the input file, in this case source.name.
        -vn disables video recording, meaning only the audio will be processed.
        -ar sets the audio sampling rate to 44100 Hz.
        -b:a sets the audio bitrate to 16k (16 kilobits per second).
        -f specifies the output format, in this case mp3.

    """
    with (
        NamedTemporaryFile('w+b') as source,
        NamedTemporaryFile('r+b') as result,
    ):

        source.write(file)
        source.flush()
        command = [
            'ffmpeg', '-y',
            '-i', source.name,
            '-ab', '16k',
            '-f', 'mp3',
            result.name,
        ]
        try:
            command_result = subprocess.run(command, check=True)
            if command_result.stderr:
                logger.error('Error while converting file to mp3, details: %s', result.stderr)
                raise EncodingError(f"Can't convert file to mp3, details: {result.stderr}")
        except subprocess.CalledProcessError as e:
            logger.error('Error while converting file to mp3, details: %s', e.stderr)
            raise EncodingError(f"Can't convert file to mp3, details: {e.stderr}")
        return result.read()
