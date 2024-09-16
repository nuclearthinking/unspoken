import uuid
import logging

import magic
from fastapi import APIRouter, UploadFile, HTTPException

from unspoken.services import db

# from unspoken.settings import settings
from unspoken.enitites.api.upload import UploadResponse

# from unspoken.services.queue.broker import celery
from unspoken.enitites.enums.mime_types import MimeType
from unspoken.services.task_queue import add_task


upload_router = APIRouter(
    prefix='/upload',
    tags=['Upload'],
)

logger = logging.getLogger(__name__)


@upload_router.post('/media')
async def upload_audio(file: UploadFile) -> UploadResponse:
    file_data = await file.read()
    file_type = magic.from_buffer(file_data[:2048], mime=True)
    if not MimeType(file_type).is_supported():
        raise HTTPException(status_code=400, detail=f'File format {file_type} is not supported.')
    temp_file = db.save_temp_file(db.TempFile(file_name=str(uuid.uuid4()), file_type=MimeType(file_type)))
    temp_file.write(file_data)
    task = db.create_new_task(uploaded_file_name=file.filename)
    logger.info('Publishing task %s', task.id)
    add_task(temp_file.id, task.id)
    return UploadResponse(
        task_id=task.id,
        task_status=task.status,
    )
