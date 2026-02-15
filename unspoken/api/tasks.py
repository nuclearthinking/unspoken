from fastapi import APIRouter, Header, HTTPException, Response

from unspoken.core.security import hash_token
from unspoken.enitites.api.tasks import TaskResponse
from unspoken.enitites.enums.task_status import TaskStatus
from unspoken.enitites.transcription import TranscriptionResult, TranscriptionSegment
from unspoken.services import db

tasks_router = APIRouter(
    prefix='/task',
    tags=['Tasks'],
)


def _check_ownership(task, token: str | None) -> bool:
    if not token or not task.owner_token_hash:
        return False
    return hash_token(token) == task.owner_token_hash


@tasks_router.get('/{task_id:int}/')
def get_task(task_id: int, x_task_token: str | None = Header(default=None)) -> TaskResponse:
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail='Task not found.')
    result = TaskResponse(
        id=task.id,
        status=task.status,
        file_name=task.uploaded_file_name,
        is_owned=_check_ownership(task, x_task_token),
    )
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


@tasks_router.delete('/{task_id:int}/')
def delete_task(task_id: int, x_task_token: str | None = Header(default=None)):
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail='Task not found.')
    if not _check_ownership(task, x_task_token):
        raise HTTPException(status_code=403, detail='You do not have permission to delete this task.')
    db.delete_task(task_id)
    return Response(status_code=204)


_SQUEEZE_MAX_PAUSE_SECONDS = 1.5
_SQUEEZE_MAX_DURATION_SECONDS = 20.0


def squeeze_messages(messages: list[TranscriptionSegment]) -> list[TranscriptionSegment]:
    """Merge consecutive segments from the same speaker into one message,
    but start a **new** message when:

    * the speaker changes,
    * the silence gap between segments exceeds ``_SQUEEZE_MAX_PAUSE_SECONDS``, or
    * the accumulated duration would exceed ``_SQUEEZE_MAX_DURATION_SECONDS``.

    This produces readable, paragraph-sized messages instead of huge walls
    of text.
    """
    if len(messages) <= 1:
        return messages

    result_messages: list[TranscriptionSegment] = []
    last_message: TranscriptionSegment | None = None

    for message in messages:
        if last_message is None:
            last_message = message.model_copy()
            continue

        gap = message.start - last_message.end
        merged_duration = message.end - last_message.start
        same_speaker = last_message.speaker == message.speaker

        should_merge = (
            same_speaker
            and gap <= _SQUEEZE_MAX_PAUSE_SECONDS
            and merged_duration <= _SQUEEZE_MAX_DURATION_SECONDS
        )

        if should_merge:
            last_message.end = message.end

            current_text = last_message.text.strip()
            next_text = message.text.strip()
            if not current_text:
                last_message.text = next_text
                continue
            if not next_text:
                continue
            if current_text[-1] in ('.', ',', '!', '?', ';', ':'):
                connection_symbol = ' '
            else:
                connection_symbol = ', '
            last_message.text = connection_symbol.join([current_text, next_text])
        else:
            result_messages.append(last_message)
            last_message = message.model_copy()

    if last_message is not None:
        result_messages.append(last_message)

    return result_messages
