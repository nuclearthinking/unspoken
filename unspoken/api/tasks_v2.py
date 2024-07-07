from fastapi import APIRouter, HTTPException

from unspoken.services import db
from unspoken.enitites.api.tasks import TaskResponseV2
from unspoken.enitites.api.messages import MessageResponse
from unspoken.enitites.api.speakers import SpeakerResponse
from unspoken.enitites.enums.task_status import TaskStatus

tasks_router = APIRouter(
    prefix='/tasks',
    tags=['Tasks'],
)


@tasks_router.get('/{task_id}/')
def get_task_messages(task_id: int) -> TaskResponseV2:
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail='Task not found.')
    response = TaskResponseV2(
        id=task_id,
        status=task.status,
        file_name=task.uploaded_file_name,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )
    if task.status != TaskStatus.completed:
        return response

    messages = db.get_task_messages(task_id)
    sorted_messages = sorted(messages, key=lambda x: x.start_time)
    speakers = db.get_task_speakers(task_id)
    response.messages = [MessageResponse.from_orm(m) for m in sorted_messages]
    response.speakers = [SpeakerResponse.from_orm(s) for s in speakers]
    return response
