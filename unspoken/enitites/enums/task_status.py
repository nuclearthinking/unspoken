from enum import Enum


class TaskStatus(str, Enum):
    queued = 'queued'
    audio_converting = 'audio_converting'
    transcribing = 'transcribing'
    completed = 'completed'
    failed = 'failed'
    unknown = None

    @classmethod
    def _missing_(cls, value):
        return cls.unknown
