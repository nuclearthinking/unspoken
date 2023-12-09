from enum import Enum


class TaskStatus(str, Enum):
    queued = 'queued'
    conversion = 'conversion'
    diarization = 'diarization'
    transcribing = 'transcribing'
    completed = 'completed'
    failed = 'failed'
    unknown = None

    @classmethod
    def _missing_(cls, value):
        return cls.unknown
