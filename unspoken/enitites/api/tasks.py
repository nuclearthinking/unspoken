from pydantic import BaseModel

from unspoken.enitites.enums.task_status import TaskStatus
from unspoken.enitites.transcription import TranscriptionSegment


class TaskResponse(BaseModel):
    id: int
    status: TaskStatus
    file_name: str = None
    speakers: list[str] = None
    messages: list[TranscriptionSegment] = None
