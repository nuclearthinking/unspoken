from fastapi import APIRouter, HTTPException

from unspoken.services import db
from unspoken.enitites.api.tasks import TaskResponse
from unspoken.enitites.transcription import TranscriptionResult
from unspoken.enitites.enums.task_status import TaskStatus

tasks_router = APIRouter(prefix='/task')


@tasks_router.get('/{id_}/')
def get_task(id_: int):
    task = db.get_task(id_)
    if not task:
        raise HTTPException(status_code=404, detail='Task not found.')
    result = TaskResponse(
        id=task.id,
        status=task.status,
    )
    if task.audio:
        result.file_name = task.audio.file_name
    if task.status != TaskStatus.completed:
        return result
    if not task.transcript:
        raise HTTPException(status_code=500, detail='Task broken.')
    if not task.transcript.transcription_result:
        raise HTTPException(status_code=500, detail='Task broken.')
    transcription_result = TranscriptionResult.parse_obj(task.transcript.transcription_result)
    speakers = {m.speaker for m in transcription_result.messages}
    result.speakers = list(speakers)
    result.messages = transcription_result.messages
    return result
