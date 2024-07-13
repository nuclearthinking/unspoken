import os
import logging
import datetime
from pathlib import Path

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship, sessionmaker, mapped_column, scoped_session, declarative_base

from alembic import command
from alembic.config import Config
from unspoken.settings import settings
from unspoken.exceptions import TranscriptNotFound
from unspoken.enitites.enums.mime_types import MimeType
from unspoken.enitites.enums.task_status import TaskStatus

logger = logging.getLogger(__name__)


def apply_migrations() -> None:
    logger.info('Applying migrations.')
    alembic_cfg = Config(settings.alembic_ini_path)
    command.upgrade(alembic_cfg, 'head')
    logger.info('Migrations completed.')


def get_database_url() -> str:
    return 'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}'.format(
        user=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        db_name=settings.db_name,
    )


engine = sa.create_engine(
    get_database_url(),
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
)
Session = scoped_session(sessionmaker(autocommit=False, bind=engine))


class Base:
    created_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)


Base = declarative_base(cls=Base)
Base.query = Session.query_property()


def setup() -> None:
    Base.metadata.create_all(checkfirst=True, bind=engine)
    apply_migrations()


class Transcript(Base):
    __tablename__ = 'transcript'

    id: Mapped[int] = mapped_column(primary_key=True)
    speach_to_text_result: Mapped[dict | list] = mapped_column(sa.JSON, nullable=True)
    diarization_result: Mapped[dict | list] = mapped_column(sa.JSON, nullable=True)
    transcription_result: Mapped[dict | list] = mapped_column(sa.JSON, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)


class TempFile(Base):
    __tablename__ = 'temp_file'

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    file_type: Mapped[MimeType] = mapped_column(
        sa.Enum(MimeType, native_enum=False, length=20),
        nullable=False,
    )

    def write(self, data: bytes) -> None:
        path = Path(settings.temp_files_dir) / self.file_name
        with open(path, 'wb') as f:
            f.write(data)

    def read(self) -> bytes:
        path = Path(settings.temp_files_dir) / self.file_name
        with open(path, 'rb') as f:
            return f.read()

    def delete(self) -> None:
        path = Path(settings.temp_files_dir) / self.file_name
        logger.info('Deleting file %s', str(path))
        os.remove(Path(settings.temp_files_dir) / self.file_name)
        if path.exists():
            logger.warning('File %s still exists after delete', str(path))
        with Session() as s:
            s.delete(self)
            s.commit()
            return


class Task(Base):
    __tablename__ = 'task'

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[TaskStatus] = mapped_column(
        sa.Enum(TaskStatus, native_enum=False),
        nullable=False,
        default=TaskStatus.queued,
    )
    uploaded_file_name: Mapped[str] = mapped_column(sa.String(255), nullable=True)
    transcript_id: Mapped[int] = mapped_column(sa.ForeignKey(Transcript.id), nullable=False)
    transcript: Mapped[Transcript] = relationship(Transcript, foreign_keys=[transcript_id], lazy='joined')


class Speaker(Base):
    __tablename__ = 'speakers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    task_id: Mapped[int] = mapped_column(sa.Integer, nullable=False)


class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    speaker_id: Mapped[int] = mapped_column(sa.ForeignKey(Speaker.id), nullable=True)
    speaker: Mapped[Speaker] = relationship(Speaker, foreign_keys=[speaker_id], lazy='joined')
    task_id: Mapped[int] = mapped_column(sa.ForeignKey(Task.id), nullable=False)
    task: Mapped[Task] = relationship(Task, foreign_keys=[task_id], lazy='joined')
    text: Mapped[str] = mapped_column(sa.Text, nullable=False)
    start_time: Mapped[float] = mapped_column(sa.Float, nullable=False)
    end_time: Mapped[float] = mapped_column(sa.Float, nullable=False)


class LabelingTask(Base):
    __tablename__ = 'labeling_tasks'

    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[bytes] = mapped_column(sa.LargeBinary, nullable=False)
    text: Mapped[str] = mapped_column(sa.Text, nullable=False)
    is_completed: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=False)


class LabelingResult(Base):
    __tablename__ = 'labeling_result'

    id: Mapped[int] = mapped_column(primary_key=True)
    labeling_task_id: Mapped[int] = mapped_column(sa.ForeignKey(LabelingTask.id), nullable=False)
    labeling_task: Mapped[LabelingTask] = relationship(LabelingTask, foreign_keys=[labeling_task_id], lazy='joined')
    text: Mapped[str] = mapped_column(sa.Text, nullable=False)


def create_speaker(name: str, task_id: int, session: Session = None) -> Speaker:
    session = session or Session()
    with session:
        speaker = Speaker(name=name, task_id=task_id)
        session.add(speaker)
        session.commit()
        session.refresh(speaker)
        return speaker


def save_messages(messages: list[Message], session: Session = None) -> None:
    session = session or Session()
    with session:
        [session.add(m) for m in messages]
        session.commit()


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
        query = sa.select(TempFile).where(TempFile.id == id_)
        return s.execute(query).scalar_one_or_none()


def get_task(id_: int, session: Session = None, detach: bool = False) -> Task | None:
    session = session or Session()
    query = sa.select(Task).where(Task.id == id_)
    with session:
        task = session.execute(query).scalar_one_or_none()
        if task is None:
            return None
        session.refresh(task)
        if detach:
            session.expunge(task)
        return task


def update_task(task: Task, session: Session = None, **kwargs) -> Task:
    session = session or Session()
    with session:
        session.add(task)
        logger.debug('Updating task %s with properties %s', task, kwargs)
        for key, value in kwargs.items():
            setattr(task, key, value)
        session.commit()
        return task


def save_speach_to_text_result(id_, result: dict, session: Session = None) -> None:
    session = session or Session()
    query = sa.select(Transcript).where(Transcript.id == id_)
    with session:
        transcript = session.execute(query).scalar_one_or_none()
        if not transcript:
            raise TranscriptNotFound(f'Transcript with id {id_} not found.')
        transcript.speach_to_text_result = result
        session.commit()


def save_diarization_result(id_, result: dict, session: Session = None) -> None:
    session = session or Session()
    query = sa.select(Transcript).where(Transcript.id == id_)
    with session:
        transcript = session.execute(query).scalar_one_or_none()
        if not transcript:
            raise TranscriptNotFound(f'Transcript with id {id_} not found.')
        transcript.diarization_result = result
        session.commit()


def save_transcription_result(id_, result: dict, session: Session = None) -> None:
    session = session or Session()
    query = sa.select(Transcript).where(Transcript.id == id_)
    with session:
        transcript = session.execute(query).scalar_one_or_none()
        if not transcript:
            raise TranscriptNotFound(f'Transcript with id {id_} not found.')
        transcript.transcription_result = result
        session.commit()


def get_message(id_: int, session: Session = None) -> Message | None:
    session = session or Session()
    query = sa.select(Message).where(Message.id == id_)
    with session:
        message = session.execute(query).scalar_one_or_none()
        if message is None:
            return None
        return message


def get_speaker(id_: int, session: Session = None) -> Speaker | None:
    session = session or Session()
    query = sa.select(Speaker).where(Speaker.id == id_)
    with session:
        speaker = session.execute(query).scalar_one_or_none()
        if speaker is None:
            return None
        return speaker


def update_speaker(speaker: Speaker, session: Session = None, **kwargs) -> Speaker:
    session = session or Session()
    with session:
        session.add(speaker)
        logger.debug('Updating speaker %s with properties %s', speaker, kwargs)
        for key, value in kwargs.items():
            setattr(speaker, key, value)
        session.commit()
        session.refresh(speaker)
        return speaker


def get_task_speakers(task_id, session: Session = None) -> list[Speaker]:
    session = session or Session()
    query = sa.select(Speaker).where(Speaker.task_id == task_id)
    with session:
        speakers = session.execute(query).scalars().all()
        return list(speakers)


def update_message(message: Message, session: Session = None, **kwargs) -> Message:
    session = session or Session()
    with session:
        session.add(message)
        logger.debug('Updating message %s with properties %s', message, kwargs)
        for key, value in kwargs.items():
            setattr(message, key, value)
        session.commit()
        session.refresh(message)
        return message


def get_task_messages(task_id, session: Session = None) -> list[Message]:
    session = session or Session()
    query = sa.select(Message).where(Message.task_id == task_id)
    with session:
        messages = session.execute(query).scalars().all()
        return list(messages)
