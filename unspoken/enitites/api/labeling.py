from typing import List

from pydantic import BaseModel

from unspoken.enitites.enums.labeling_task_status import LabelingTaskStatus
from unspoken.enitites.enums.labeling_segment_status import LabelingSegmentStatus


class LabelingSpeakerResponse(BaseModel):
    id: int
    name: str


class LabelingSegmentResponse(BaseModel):
    id: int
    start: float
    end: float
    text: str
    speaker: LabelingSpeakerResponse
    status: LabelingSegmentStatus

    class Config:
        from_attributes = True


class LabelingTaskResponse(BaseModel):
    id: int
    transcript_id: int
    file_name: str
    status: LabelingTaskStatus
    segments: List[LabelingSegmentResponse]
    speakers: List[LabelingSpeakerResponse]

    class Config:
        from_attributes = True


class UpdateLabelingSegmentRequest(BaseModel):
    status: LabelingSegmentStatus
    start: float
    end: float
    text: str
    speaker: LabelingSpeakerResponse
