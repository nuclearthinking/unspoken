from enum import Enum


class TaskStatus(str, Enum):
    queued = 'queued'
    processing = 'processing'
    completed = 'completed'
    failed = 'failed'
    unknown = None

    @classmethod
    def _missing_(cls, value):
        return cls.unknown
