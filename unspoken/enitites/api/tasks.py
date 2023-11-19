from pydantic import BaseModel

from unspoken.enitites.transcription import TranscriptionSegment
from unspoken.enitites.enums.task_status import TaskStatus


class TaskResponse(BaseModel):
    id: int
    status: TaskStatus
    file_name: str = None
    speakers: list[str] = None
    messages: list[TranscriptionSegment] = None
