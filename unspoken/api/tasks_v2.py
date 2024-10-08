from fastapi import APIRouter, HTTPException

from unspoken.enitites.api.messages import MessageResponse
from unspoken.enitites.api.speakers import SpeakerResponse
from unspoken.enitites.api.tasks import TaskResponseV2
from unspoken.enitites.enums.task_status import TaskStatus
from unspoken.services import db

tasks_router = APIRouter(
    prefix='/tasks',
    tags=['Tasks'],
)


@tasks_router.get('/{task_id:int}/')
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
    if not messages:
        raise HTTPException(status_code=404, detail='No messages found for task.')

    sorted_messages = sorted(messages, key=lambda x: x.start_time)

    speakers = db.get_task_speakers(task_id)
    if not speakers:
        raise HTTPException(status_code=404, detail='No speakers found for task.')

    response.messages = [MessageResponse.model_validate(m) for m in sorted_messages]
    response.speakers = [SpeakerResponse.model_validate(s) for s in speakers]
    return response
