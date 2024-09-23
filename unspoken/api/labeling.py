import io
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from unspoken.services import db
from unspoken.enitites.api.labeling import (
    LabelingTaskResponse,
    LabelingSegmentResponse,
    LabelingSpeakerResponse,
    UpdateLabelingSegmentRequest
)
from unspoken.services.audio_service import AudioService

logger = logging.getLogger(__name__)

labeling_router = APIRouter(prefix='/labeling', tags=['Labeling'])


@labeling_router.get('/task/{task_id}')
def get_labeling_task(task_id: int) -> LabelingTaskResponse:
    logger.info(f'Getting labeling task for task ID: {task_id}')
    labeling_task = db.get_labeling_task_by_task_id(task_id)
    if not labeling_task:
        logger.error(f'Labeling task not found for task ID: {task_id}')
        raise HTTPException(status_code=404, detail='Labeling task not found.')

    segments = [LabelingSegmentResponse.model_validate(segment) for segment in labeling_task.segments]
    speakers = [LabelingSpeakerResponse.model_validate(speaker) for speaker in labeling_task.speakers]

    logger.info(f'Returning labeling task for task ID: {task_id}')
    return LabelingTaskResponse(
        id=labeling_task.id,
        file_name=labeling_task.file_name,
        status=labeling_task.status,
        segments=segments,
        speakers=speakers,
    )


@labeling_router.post('/task/{task_id}/segment/{segment_id}')
def update_labeling_segment(
    task_id: int,
    segment_id: int,
    request: UpdateLabelingSegmentRequest,
) -> LabelingSegmentResponse:
    labeling_task = db.get_labeling_task_by_task_id(task_id)
    if not labeling_task:
        raise HTTPException(status_code=404, detail='Labeling task not found.')

    segment = next(
        (segment for segment in labeling_task.segments if segment.id == segment_id),
        None,
    )
    if not segment:
        raise HTTPException(status_code=404, detail='Segment not found.')

    updated_segment = db.update_labeling_segment(
        segment_id=segment.id,
        status=request.status,
    )

    return LabelingSegmentResponse.model_validate(updated_segment)


@labeling_router.get('/task/{task_id}/segment/{segment_id}/audio')
def get_segment_audio(task_id: int, segment_id: int):
    labeling_task = db.get_labeling_task_by_task_id(task_id)
    if not labeling_task:
        raise HTTPException(status_code=404, detail='Labeling task not found.')

    segment = next(
        (segment for segment in labeling_task.segments if segment.id == segment_id),
        None,
    )
    if not segment:
        raise HTTPException(status_code=404, detail='Segment not found.')

    mp3_data = AudioService.trim_mp3(
        mp3_data=labeling_task.audio_data,
        start=segment.start,
        end=segment.end,
    )

    return StreamingResponse(io.BytesIO(mp3_data), media_type='audio/mpeg')
