import logging
import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, DeclarativeBase, relationship, sessionmaker, mapped_column, scoped_session

from unspoken.settings import settings
from unspoken.exceptions import TranscriptNotFound
from unspoken.enitites.enums.task_status import TaskStatus

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


class Base(DeclarativeBase):
    pass


def setup() -> None:
    Base.metadata.create_all(checkfirst=True, bind=engine)


class Audio(Base):
    __tablename__ = 'audio'

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    mp3_data: Mapped[bytes] = mapped_column(sa.LargeBinary, nullable=False)
    wav_data: Mapped[bytes] = mapped_column(sa.LargeBinary, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)


class Transcript(Base):
    __tablename__ = 'transcript'

    id: Mapped[int] = mapped_column(primary_key=True)
    speach_to_text_result: Mapped[dict | list] = mapped_column(sa.JSON, nullable=True)
    diarization_result: Mapped[dict | list] = mapped_column(sa.JSON, nullable=True)
    transcription_result: Mapped[dict | list] = mapped_column(sa.JSON, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)


class Task(Base):
    __tablename__ = 'task'

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[TaskStatus] = mapped_column(
        sa.Enum(TaskStatus, native_enum=False),
        nullable=False,
        default=TaskStatus.queued,
    )
    audio_id: Mapped[int] = mapped_column(sa.ForeignKey(Audio.id), nullable=True)
    audio: Mapped[Audio] = relationship(Audio, foreign_keys=[audio_id], lazy='joined')
    transcript_id: Mapped[int] = mapped_column(sa.ForeignKey(Transcript.id), nullable=False)
    transcript: Mapped[Transcript] = relationship(Transcript, foreign_keys=[transcript_id], lazy='joined')


class TempFile(Base):
    __tablename__ = 'temp_file'

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(sa.ForeignKey(Task.id), nullable=False)
    file_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    data: Mapped[bytes] = mapped_column(sa.LargeBinary, nullable=False)


def create_new_task() -> Task:
    task = Task(
        transcript=Transcript(),
    )
    Session.add(task)
    Session.commit()
    return task


def save_temp_file(file: TempFile) -> TempFile:
    Session.add(file)
    Session.commit()
    return file


def get_temp_file(id_: int) -> TempFile | None:
    query = sa.select(TempFile).where(TempFile.id == id_)
    return Session.execute(query).scalar_one_or_none()


def remove_temp_file(id_: int) -> None:
    query = sa.delete(TempFile).where(TempFile.id == id_)
    Session.execute(query)
    Session.commit()
    logger.info(f'Removed temp file with id {id_}')


def create_audio(audio: Audio) -> Audio:
    Session.add(audio)
    Session.commit()
    return audio


def get_task(id_: int) -> Task | None:
    query = sa.select(Task).where(Task.id == id_)
    return Session.execute(query).scalar_one_or_none()


def update_task(task: Task, **kwargs) -> Task:
    for key, value in kwargs.items():
        setattr(task, key, value)
    Session.commit()
    return task


def save_speach_to_text_result(id_, result: dict) -> None:
    query = sa.select(Transcript).where(Transcript.id == id_)
    transcript = Session.execute(query).scalar_one_or_none()
    if not transcript:
        raise TranscriptNotFound(f'Transcript with id {id_} not found.')
    transcript.speach_to_text_result = result
    Session.commit()


def save_diarization_result(id_, result: dict) -> None:
    query = sa.select(Transcript).where(Transcript.id == id_)
    transcript = Session.execute(query).scalar_one_or_none()
    if not transcript:
        raise TranscriptNotFound(f'Transcript with id {id_} not found.')
    transcript.diarization_result = result
    Session.commit()


def save_transcription_result(id_, result: dict) -> None:
    query = sa.select(Transcript).where(Transcript.id == id_)
    transcript = Session.execute(query).scalar_one_or_none()
    if not transcript:
        raise TranscriptNotFound(f'Transcript with id {id_} not found.')
    transcript.transcription_result = result
    Session.commit()
