import logging

import magic
from fastapi import APIRouter, UploadFile, HTTPException

from unspoken.services import db
from unspoken.enitites.api.upload import UploadResponse
from unspoken.services.queue.tasks import convert_audio
from unspoken.enitites.enums.mime_types import MimeType

upload_router = APIRouter(prefix='/upload')

logger = logging.getLogger(__name__)


@upload_router.post('/audio', response_model=UploadResponse)
async def upload_audio(file: UploadFile):
    file_data = await file.read()
    file_type = magic.from_buffer(file_data[:2048], mime=True)
    if not MimeType(file_type).is_audio():
        raise HTTPException(status_code=400, detail='File is not audio.')
    task = db.create_new_task()
    temp_file = db.save_temp_file(db.TempFile(file_name=file.filename, data=file_data, task_id=task.id))
    logger.info('Publishing convert audio task for temp_file_id %s', temp_file.id)
    convert_audio.delay(temp_file.id)
    return UploadResponse(
        task_id=task.id,
        task_status=task.status,
    )
