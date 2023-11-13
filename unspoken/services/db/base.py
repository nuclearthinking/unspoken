import datetime
import logging

import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import BLOB
from sqlalchemy.orm import (
    Mapped,
    DeclarativeBase,
    sessionmaker,
    mapped_column,
    scoped_session
)

logger = logging.getLogger(__name__)

engine = sa.create_engine("sqlite:///unspoken.db")
session = scoped_session(sessionmaker(autocommit=False, bind=engine))


class Base(DeclarativeBase):
    pass


def setup() -> None:
    Base.metadata.create_all(checkfirst=True, bind=engine)


class Audio(Base):
    __tablename__ = "audio"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    data: Mapped[bytes] = mapped_column(BLOB, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
