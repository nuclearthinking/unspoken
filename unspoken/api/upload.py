import uuid
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
    if not MimeType(file_type).is_supported():
        raise HTTPException(status_code=400, detail=f'File format {file_type} is not supported.')
    temp_file = db.save_temp_file(db.TempFile(file_name=uuid.uuid4(), file_type=file_type))
    temp_file.write(file_data)
    task = db.create_new_task(uploaded_file_name=file.filename)
    logger.info('Publishing convert audio task for temp_file_id %s', temp_file.id)
    convert_audio.delay(temp_file_id=temp_file.id, task_id=task.id)
    return UploadResponse(
        task_id=task.id,
        task_status=task.status,
    )
