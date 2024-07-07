from fastapi import APIRouter, HTTPException

from unspoken.services import db
from unspoken.enitites.api.tasks import TaskResponse
from unspoken.enitites.transcription import TranscriptionResult, TranscriptionSegment
from unspoken.enitites.enums.task_status import TaskStatus

tasks_router = APIRouter(
    prefix='/task',
    tags=['Tasks'],
)


@tasks_router.get('/{task_id}/')
def get_task(task_id: int) -> TaskResponse:
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail='Task not found.')
    result = TaskResponse(id=task.id, status=task.status, file_name=task.uploaded_file_name)
    if task.status != TaskStatus.completed:
        return result
    if not task.transcript:
        raise HTTPException(status_code=500, detail='Task broken.')
    if not task.transcript.transcription_result:
        raise HTTPException(status_code=500, detail='Task broken.')
    transcription_result = TranscriptionResult.parse_obj(task.transcript.transcription_result)
    speakers = {m.speaker for m in transcription_result.messages}
    result.speakers = list(speakers)
    result.messages = squeeze_messages(transcription_result.messages)
    return result


def squeeze_messages(messages: list[TranscriptionSegment]) -> list[TranscriptionSegment]:
    if len(messages) <= 1:
        return messages

    _messages = messages[:]
    result_messages = []
    last_message = None
    while _messages:
        message = _messages.pop(0)
        if not last_message:
            last_message = message
            continue

        if last_message.speaker == message.speaker:
            if last_message.text.endswith(',') or last_message.text.endswith('.'):
                connection_symbol = ' '
            else:
                connection_symbol = ', '
            last_message.text = connection_symbol.join([last_message.text, message.text])
            continue
        else:
            result_messages.append(last_message)
            last_message = message
            continue
    result_messages.append(last_message)

    return result_messages
