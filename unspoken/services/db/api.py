import logging

from sqlalchemy import delete, select

from unspoken.exceptions import TranscriptNotFound
from unspoken.services.db.models import Task, Session, TempFile, Transcript

logger = logging.getLogger(__name__)


def create_new_task(**kwargs) -> Task:
    with Session() as s:
        task = Task(
            transcript=Transcript(),
            **kwargs,
        )
        s.add(task)
        s.commit()
        s.refresh(task)
        return task


def save_temp_file(file: TempFile) -> TempFile:
    with Session() as s:
        s.add(file)
        s.commit()
        s.refresh(file)
        return file


def get_temp_file(id_: int) -> TempFile | None:
    with Session() as s:
        query = select(TempFile).where(TempFile.id == id_)
        return s.execute(query).scalar_one_or_none()


def remove_temp_file(id_: int) -> None:
    with Session() as s:
        query = delete(TempFile).where(TempFile.id == id_)
        s.execute(query)
        s.commit()
        logger.info(f'Removed temp file with id {id_}')


def get_task(id_: int) -> Task | None:
    query = select(Task).where(Task.id == id_)
    task = Session.execute(query).scalar_one_or_none()
    if task is None:
        return None
    Session.refresh(task)
    return task


def update_task(task: Task, **kwargs) -> Task:
    Session.add(task)
    logger.info('Updating task %s with properties %s', task, kwargs)
    for key, value in kwargs.items():
        setattr(task, key, value)
    Session.commit()
    return task


def save_speach_to_text_result(id_, result: dict) -> None:
    query = select(Transcript).where(Transcript.id == id_)
    transcript = Session.execute(query).scalar_one_or_none()
    if not transcript:
        raise TranscriptNotFound(f'Transcript with id {id_} not found.')
    transcript.speach_to_text_result = result
    Session.commit()


def save_diarization_result(id_, result: dict) -> None:
    query = select(Transcript).where(Transcript.id == id_)
    transcript = Session.execute(query).scalar_one_or_none()
    if not transcript:
        raise TranscriptNotFound(f'Transcript with id {id_} not found.')
    transcript.diarization_result = result
    Session.commit()


def save_transcription_result(id_, result: dict) -> None:
    query = select(Transcript).where(Transcript.id == id_)
    transcript = Session.execute(query).scalar_one_or_none()
    if not transcript:
        raise TranscriptNotFound(f'Transcript with id {id_} not found.')
    transcript.transcription_result = result
    Session.commit()
