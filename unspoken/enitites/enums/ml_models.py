from enum import Enum

from unspoken.settings import settings


class Model(Enum):
    large_v3 = 'large-v3'
    diarization = 'diarization'
    speechbrain = 'speechbrain'

    def path(self) -> str:
        return f'{settings.models_dir_path}/{self.value}'
