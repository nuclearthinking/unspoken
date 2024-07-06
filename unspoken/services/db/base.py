import datetime
import logging
import os
from pathlib import Path

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship, sessionmaker, mapped_column, scoped_session, declarative_base

from unspoken.enitites.enums.mime_types import MimeType
from unspoken.enitites.enums.task_status import TaskStatus
from unspoken.exceptions import TranscriptNotFound
from unspoken.settings import settings

logger = logging.getLogger(__name__)

engine = sa.create_engine(
    'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}'.format(
        user=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        db_name=settings.db_name,
    ),
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
)
Session = scoped_session(sessionmaker(autocommit=False, bind=engine))
Base = declarative_base()
Base.query = Session.query_property()


def setup() -> None:
    Base.metadata.create_all(checkfirst=True, bind=engine)


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
    created_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)


class Speaker(Base):
    __tablename__ = 'speakers'

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    task_id: Mapped[int] = mapped_column(sa.Integer, nullable=False)


class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    speaker_id: Mapped[int] = mapped_column(sa.ForeignKey(Speaker.id), nullable=True)
    speaker: Mapped[Speaker] = relationship(Speaker, foreign_keys=[speaker_id], lazy='joined')
    task_id: Mapped[int] = mapped_column(sa.ForeignKey(Task.id), nullable=False)
    task: Mapped[Task] = relationship(Task, foreign_keys=[task_id], lazy='joined')
    text: Mapped[str] = mapped_column(sa.Text, nullable=False)
    start_time: Mapped[float] = mapped_column(sa.Float, nullable=False)
    end_time: Mapped[float] = mapped_column(sa.Float, nullable=False)


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
