import datetime
import json
import logging
import os
import traceback
from pathlib import Path

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship, scoped_session, sessionmaker

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from unspoken.enitites.enums.mime_types import MimeType
from unspoken.enitites.enums.task_status import TaskStatus
from unspoken.exceptions import TranscriptNotFound
from unspoken.settings import settings

logger = logging.getLogger(__name__)


def apply_migrations() -> None:
    logger.info('Starting migration process.')
    try:
        alembic_cfg = Config(settings.alembic_ini_path)
        logger.info(f'Alembic config loaded from: {settings.alembic_ini_path}')

        script = ScriptDirectory.from_config(alembic_cfg)

        with engine.connect() as connection:
            table_exists_query = """
                        SELECT COUNT(*) 
                        FROM information_schema.tables 
                        WHERE table_name = 'alembic_version'
                        """
            table_exists = connection.execute(sa.text(table_exists_query)).scalar() > 0

            if table_exists:
                current_rev = connection.execute(sa.text('SELECT version_num FROM alembic_version')).scalar()
                logger.info(f'Found existing database schema with revision: {current_rev}')
            else:
                logger.warning('alembic_version table not found. Assuming clean database.')
                current_rev = None

        head_rev = script.get_current_head()

        if current_rev != head_rev:
            logger.info(f'Current revision: {current_rev}, upgrading to: {head_rev}')
            command.upgrade(alembic_cfg, 'head')
            logger.info('Migrations completed successfully.')
        else:
            logger.info(f'Database is already at head revision: {head_rev}. Skipping Alembic operations.')

    except Exception as e:
        logger.error(f'Error during migration: {str(e)}')
        logger.error(traceback.format_exc())
        raise
    finally:
        logger.info('Migration process finished.')


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
    json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False),
    json_deserializer=json.loads,
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
        try:
            os.remove(path)
        except FileNotFoundError:
            logger.warning('File %s was already removed from disk.', str(path))
        if path.exists():
            logger.warning('File %s still exists after delete.', str(path))
        with Session() as s:
            s.delete(self)
            s.commit()


class Task(Base):
    __tablename__ = 'task'

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[TaskStatus] = mapped_column(
        sa.Enum(TaskStatus, native_enum=False),
        nullable=False,
        default=TaskStatus.queued,
    )
    uploaded_file_name: Mapped[str] = mapped_column(sa.String(255), nullable=True)
    owner_token_hash: Mapped[str] = mapped_column(sa.String(64), nullable=True)
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
    _own_session = session is None
    session = session or Session()
    try:
        speaker = Speaker(name=name, task_id=task_id)
        session.add(speaker)
        if _own_session:
            session.commit()
        else:
            session.flush()
        session.refresh(speaker)
        return speaker
    finally:
        if _own_session:
            session.close()


def save_messages(messages: list[Message], session: Session = None) -> None:
    _own_session = session is None
    session = session or Session()
    try:
        for m in messages:
            session.add(m)
        if _own_session:
            session.commit()
        else:
            session.flush()
    finally:
        if _own_session:
            session.close()


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
    _own_session = session is None
    session = session or Session()
    try:
        query = sa.select(Task).where(Task.id == id_)
        task = session.execute(query).scalar_one_or_none()
        if task is None:
            return None
        session.refresh(task)
        if detach:
            session.expunge(task)
        return task
    finally:
        if _own_session:
            session.close()


def update_task(task: Task, session: Session = None, **kwargs) -> Task:
    _own_session = session is None
    session = session or Session()
    try:
        session.add(task)
        logger.debug('Updating task %s with properties %s', task, kwargs)
        for key, value in kwargs.items():
            setattr(task, key, value)
        if _own_session:
            session.commit()
        else:
            session.flush()
        return task
    finally:
        if _own_session:
            session.close()


def save_speach_to_text_result(id_, result: dict, session: Session = None) -> None:
    _own_session = session is None
    session = session or Session()
    try:
        query = sa.select(Transcript).where(Transcript.id == id_)
        transcript = session.execute(query).scalar_one_or_none()
        if not transcript:
            raise TranscriptNotFound(f'Transcript with id {id_} not found.')
        transcript.speach_to_text_result = result
        if _own_session:
            session.commit()
        else:
            session.flush()
    finally:
        if _own_session:
            session.close()


def save_diarization_result(id_, result: dict, session: Session = None) -> None:
    _own_session = session is None
    session = session or Session()
    try:
        query = sa.select(Transcript).where(Transcript.id == id_)
        transcript = session.execute(query).scalar_one_or_none()
        if not transcript:
            raise TranscriptNotFound(f'Transcript with id {id_} not found.')
        transcript.diarization_result = result
        if _own_session:
            session.commit()
        else:
            session.flush()
    finally:
        if _own_session:
            session.close()


def save_transcription_result(id_, result: dict, session: Session = None) -> None:
    _own_session = session is None
    session = session or Session()
    try:
        query = sa.select(Transcript).where(Transcript.id == id_)
        transcript = session.execute(query).scalar_one_or_none()
        if not transcript:
            raise TranscriptNotFound(f'Transcript with id {id_} not found.')
        transcript.transcription_result = result
        if _own_session:
            session.commit()
        else:
            session.flush()
    finally:
        if _own_session:
            session.close()


def get_message(id_: int, session: Session = None) -> Message | None:
    _own_session = session is None
    session = session or Session()
    try:
        query = sa.select(Message).where(Message.id == id_)
        message = session.execute(query).scalar_one_or_none()
        return message
    finally:
        if _own_session:
            session.close()


def get_speaker(id_: int, session: Session = None) -> Speaker | None:
    _own_session = session is None
    session = session or Session()
    try:
        query = sa.select(Speaker).where(Speaker.id == id_)
        speaker = session.execute(query).scalar_one_or_none()
        return speaker
    finally:
        if _own_session:
            session.close()


def update_speaker(speaker: Speaker, session: Session = None, **kwargs) -> Speaker:
    _own_session = session is None
    session = session or Session()
    try:
        session.add(speaker)
        logger.debug('Updating speaker %s with properties %s', speaker, kwargs)
        for key, value in kwargs.items():
            setattr(speaker, key, value)
        if _own_session:
            session.commit()
        else:
            session.flush()
        session.refresh(speaker)
        return speaker
    finally:
        if _own_session:
            session.close()


def get_task_speakers(task_id, session: Session = None) -> list[Speaker]:
    _own_session = session is None
    session = session or Session()
    try:
        query = sa.select(Speaker).where(Speaker.task_id == task_id)
        speakers = session.execute(query).scalars().all()
        return list(speakers)
    finally:
        if _own_session:
            session.close()


def update_message(message: Message, session: Session = None, **kwargs) -> Message:
    _own_session = session is None
    session = session or Session()
    try:
        session.add(message)
        logger.debug('Updating message %s with properties %s', message, kwargs)
        for key, value in kwargs.items():
            setattr(message, key, value)
        if _own_session:
            session.commit()
        else:
            session.flush()
        session.refresh(message)
        return message
    finally:
        if _own_session:
            session.close()


def get_task_messages(task_id, session: Session = None) -> list[Message]:
    _own_session = session is None
    session = session or Session()
    try:
        query = sa.select(Message).where(Message.task_id == task_id)
        messages = session.execute(query).scalars().all()
        return list(messages)
    finally:
        if _own_session:
            session.close()


def delete_task(task_id: int) -> None:
    with Session() as s:
        task = s.execute(sa.select(Task).where(Task.id == task_id)).scalar_one_or_none()
        if task is None:
            return
        transcript_id = task.transcript_id
        s.execute(sa.delete(Message).where(Message.task_id == task_id))
        s.execute(sa.delete(Speaker).where(Speaker.task_id == task_id))
        s.execute(sa.delete(Task).where(Task.id == task_id))
        if transcript_id:
            s.execute(sa.delete(Transcript).where(Transcript.id == transcript_id))
        s.commit()
        logger.info('Deleted task %s and all associated data.', task_id)