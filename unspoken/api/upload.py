import magic
from fastapi import APIRouter, UploadFile, HTTPException

from unspoken.enitites.enums.mime_types import MimeType
from unspoken.exceptions import EncodingError
from unspoken.services.audio.converter import convert_to_mp3

upload_router = APIRouter(prefix='/upload')


@upload_router.post('/audio')
async def upload_audio(file: UploadFile):
    file_data = await file.read()
    file_type = magic.from_buffer(file_data[:2048], mime=True)
    if not MimeType(file_type).is_audio():
        raise HTTPException(status_code=400, detail='File is not audio.')
    try:
        result = convert_to_mp3(file_data)
    except EncodingError as e:
        raise HTTPException(status_code=400, detail=f'Unable to convert audio to mp3 format.') from e
    return {**file.__dict__, 'type': file_type}
