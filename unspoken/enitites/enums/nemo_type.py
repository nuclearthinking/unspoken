from enum import Enum
from pathlib import Path

CONFIG_MAP = {
    'meeting': 'meeting.yaml',
    'general': 'general.yaml',
    'telephonic': 'telephonic.yaml',
}


class NemoDomainType(str, Enum):
    meeting = 'meeting'
    general = 'general'
    telephonic = 'telephonic'

    def get_config_path(self) -> Path:
        path = Path.cwd() / 'resources' / 'diarization' / CONFIG_MAP[self.value]
        assert path.exists(), f'Path {path} does not exists.'
        return path
