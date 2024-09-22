from typing import List

from pydantic import BaseModel

from unspoken.enitites.enums.labeling_task_status import LabelingTaskStatus
from unspoken.enitites.enums.labeling_segment_status import LabelingSegmentStatus


class LabelingSegmentResponse(BaseModel):
    id: int
    start: float
    end: float
    text: str
    speaker: str
    status: LabelingSegmentStatus

    class Config:
        orm_mode = True


class LabelingTaskResponse(BaseModel):
    id: int
    transcript_id: int
    file_name: str
    status: LabelingTaskStatus
    segments: List[LabelingSegmentResponse]

    class Config:
        orm_mode = True


class UpdateLabelingSegmentRequest(BaseModel):
    status: LabelingSegmentStatus
    start: float
    end: float
    text: str
    speaker: str
