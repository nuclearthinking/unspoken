from enum import Enum


class LabelingTaskStatus(str, Enum):
    queued = 'queued'
    labeling = 'labeling'
    done = 'done'
