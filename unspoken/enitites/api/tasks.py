import datetime

from pydantic import Field, BaseModel

from unspoken.enitites.api.messages import MessageResponse
from unspoken.enitites.api.speakers import SpeakerResponse
from unspoken.enitites.transcription import TranscriptionSegment
from unspoken.enitites.enums.task_status import TaskStatus


class TaskResponse(BaseModel):
    id: int
    status: TaskStatus
    file_name: str = None
    speakers: list[str] = None
    messages: list[TranscriptionSegment] = None


class TaskResponseV2(BaseModel):
    messages: list[MessageResponse] = Field(default_factory=list)
    id: int
    status: TaskStatus
    file_name: str = None
    speakers: list[SpeakerResponse] = Field(default_factory=list)
    created_at: datetime.datetime
    updated_at: datetime.datetime
