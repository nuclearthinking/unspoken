from fastapi import APIRouter, HTTPException

from unspoken.enitites.api.messages import MessageResponse, UpdateMessageSpeakerRequest
from unspoken.services import db

messages_router = APIRouter(prefix='/messages', tags=['Messages'])


@messages_router.patch('/{message_id:int}/speaker')
def update_message_speaker(message_id: int, request_speaker: UpdateMessageSpeakerRequest) -> MessageResponse:
    message = db.get_message(message_id)
    if not message:
        raise HTTPException(status_code=404, detail='Message not found.')

    speaker = db.get_speaker(request_speaker.speaker_id)
    if not speaker:
        raise HTTPException(status_code=404, detail='Speaker not found.')

    if message.task_id != speaker.task_id:
        raise HTTPException(
            status_code=400,
            detail='Speaker and message have different task ids.',
        )

    message = db.update_message(message, speaker_id=request_speaker.speaker_id)
    return MessageResponse.from_orm(message)
