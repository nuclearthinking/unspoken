from fastapi import APIRouter, HTTPException

from unspoken.services import db
from unspoken.enitites.api.speakers import SpeakerResponse, UpdateSpeakerNameRequest

speakers_router = APIRouter(
    prefix='/speakers',
    tags=['Speakers'],
)


@speakers_router.patch('/{speaker_id:int}/name')
def update_speaker_name(speaker_id: int, request: UpdateSpeakerNameRequest) -> SpeakerResponse:
    speaker = db.get_speaker(speaker_id)
    if not speaker:
        raise HTTPException(status_code=404, detail='Speaker not found.')
    speaker = db.update_speaker(speaker, name=request.name)
    return SpeakerResponse.from_orm(speaker)
