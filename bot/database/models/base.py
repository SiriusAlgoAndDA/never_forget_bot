import datetime
import uuid

from sqlalchemy import Column, orm
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.sql import func

from bot.database import DeclarativeBase


class BaseModel(DeclarativeBase):
    __abstract__ = True

    id: orm.Mapped[uuid.UUID | str] = Column(  # type: ignore
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        unique=True,
        doc='Unique index of element (type UUID)',
    )
    dt_created: orm.Mapped[datetime.datetime] = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),  # pylint: disable=not-callable  # noqa: E501
        nullable=False,
        doc='Date and time of create (type TIMESTAMP)',
    )
    dt_updated: orm.Mapped[datetime.datetime] = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),  # pylint: disable=not-callable  # noqa: E501
        onupdate=func.current_timestamp(),  # pylint: disable=not-callable
        nullable=False,
        doc='Date and time of last update (type TIMESTAMP)',
    )

    def __repr__(self) -> str:
        columns = {column.name: getattr(self, column.name) for column in self.__table__.columns}  # type: ignore
        return (
            f'<{self.__tablename__}: '  # type: ignore
            f'{', '.join([f"{x[0]}={x[1]}" for x in columns.items()])}>'
        )
