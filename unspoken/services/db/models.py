import os
import logging
from pathlib import Path
from datetime import datetime

from sqlalchemy import JSON, Enum, Text, String, Integer, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import Mapped, relationship, sessionmaker, mapped_column, scoped_session, declarative_base

from unspoken.settings import settings
from unspoken.enitites.enums.mime_types import MimeType
from unspoken.enitites.enums.task_status import TaskStatus

logger = logging.getLogger(__name__)

engine = create_engine(
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
    speach_to_text_result: Mapped[dict | list] = mapped_column(JSON, nullable=True)
    diarization_result: Mapped[dict | list] = mapped_column(JSON, nullable=True)
    transcription_result: Mapped[dict | list] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class TempFile(Base):
    __tablename__ = 'temp_file'

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[MimeType] = mapped_column(
        Enum(MimeType, native_enum=False, length=20),
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
        os.remove(Path(settings.temp_files_dir) / self.file_name)
        with Session() as s:
            s.delete(self)
            s.commit()
            return


class Task(Base):
    __tablename__ = 'task'

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, native_enum=False),
        nullable=False,
        default=TaskStatus.queued,
    )
    uploaded_file_name: Mapped[str] = mapped_column(String(255), nullable=True)
    wav_file_id: Mapped[int] = mapped_column(ForeignKey(TempFile.id), nullable=True)
    wav_file: Mapped[TempFile] = relationship(TempFile, foreign_keys=[wav_file_id], lazy='joined')
    transcript_id: Mapped[int] = mapped_column(ForeignKey(Transcript.id), nullable=False)
    transcript: Mapped[Transcript] = relationship(Transcript, foreign_keys=[transcript_id], lazy='joined')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class Speaker(Base):
    __tablename__ = 'speakers'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey(Task.id), nullable=False)
    task: Mapped[Task] = relationship(Task, foreign_keys=[task_id], lazy='joined')
    speaker_id: Mapped[int] = mapped_column(ForeignKey(Speaker.id), nullable=False)
    speaker: Mapped[Speaker] = relationship(Speaker, foreign_keys=[speaker_id], lazy='joined')
    start: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
