from typing import List

from unspoken import exceptions
from unspoken.services import db
from unspoken.entities.db.labeling import LabelingSegment


class LabelingService:
    def __init__(self): ...

    def merge_segments(self, task_id: int, segment_ids: List[int]) -> LabelingSegment:
        if len(segment_ids) != 2:
            raise exceptions.UnableToMergeLabelingSegments('Only two segments allowed to merge.')

        labeling_task = db.get_labeling_task_by_task_id(task_id)
        if not labeling_task:
            raise exceptions.LabelingTaskNotFound('Labeling task not found.')

        segments_to_merge = [segment for segment in labeling_task.segments if segment.id in segment_ids]

        if len(segments_to_merge) != len(segment_ids):
            raise ValueError('One or more segment IDs are invalid.')

        # Sort segments based on start time
        segments_to_merge.sort(key=lambda segment: segment.start)

        # Check if there are any segments between the segments to merge
        segments_between = [
            segment
            for segment in labeling_task.segments
            if segment.start >= segments_to_merge[0].start
            and segment.end <= segments_to_merge[1].start
            and segment not in segments_to_merge
        ]
        if segments_between:
            raise exceptions.UnableToMergeLabelingSegments('There are segments between the segments to merge.')

        # Perform merge logic
        new_start_time = segments_to_merge[0].start
        new_end_time = segments_to_merge[-1].end
        new_text = ' '.join(segment.text for segment in segments_to_merge)

        # Create new merged segment
        new_segment = db.create_labeling_segment(
            task_id=task_id, start_time=new_start_time, end_time=new_end_time, text=new_text
        )

        # Delete old segments
        for segment in segments_to_merge:
            db.delete_labeling_segment(segment.id)

        return new_segment


def get_labeling_service():
    return LabelingService()
