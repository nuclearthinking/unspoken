from enum import Enum


class LabelingSegmentStatus(str, Enum):
    in_progress = 'in_progress'
    done = 'done'
