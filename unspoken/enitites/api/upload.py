from pydantic import BaseModel

from unspoken.enitites.enums.task_status import TaskStatus


class UploadResponse(BaseModel):
    task_id: int
    task_status: TaskStatus
