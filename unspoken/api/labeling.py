from fastapi import APIRouter, HTTPException

from unspoken.services import db
from unspoken.enitites.api.labeling import LabelingTaskResponse, LabelingSegmentResponse, UpdateLabelingSegmentRequest

labeling_router = APIRouter(prefix='/labeling', tags=['Labeling'])


@labeling_router.get('/task/{task_id}')
def get_labeling_task(task_id: int) -> LabelingTaskResponse:
    labeling_task = db.get_labeling_task_by_task_id(task_id)
    if not labeling_task:
        raise HTTPException(status_code=404, detail='Labeling task not found.')

    segments = [LabelingSegmentResponse.from_orm(segment) for segment in labeling_task.segments]

    return LabelingTaskResponse(
        id=labeling_task.id,
        transcript_id=labeling_task.transcript_id,
        file_name=labeling_task.file_name,
        status=labeling_task.status,
        segments=segments,
    )


@labeling_router.post('/task/{task_id}/segment/{segment_id}')
def update_labeling_segment(
    task_id: int,
    segment_id: int,
    request: UpdateLabelingSegmentRequest,
):
    labeling_task = db.get_labeling_task_by_task_id(task_id)
    if not labeling_task:
        raise HTTPException(status_code=404, detail='Labeling task not found.')

    segment = next(
        (segment for segment in labeling_task.segments if segment.id == segment_id),
        None,
    )
    if not segment:
        raise HTTPException(status_code=404, detail='Segment not found.')

    db.update_labeling_segment(
        segment_id=segment.id,
        status=request.status,
    )

    return {'message': 'Segment updated successfully.'}
