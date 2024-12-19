import sqlalchemy as sa
from sqlalchemy import orm

from .base import BaseModel


class User(BaseModel):
    __tablename__ = 'user'

    tg_id: orm.Mapped[str] = sa.Column(
        'tg_id',
        sa.String,
        nullable=False,
        unique=True,
        index=True,
        doc='Telegram id.',
    )
    tg_username: orm.Mapped[str] = sa.Column(
        'tg_username',
        sa.String,
        nullable=True,
        unique=True,
        index=True,
        doc='Telegram username.',
    )
    tg_name: orm.Mapped[str] = sa.Column(
        'tg_name',
        sa.String,
        nullable=True,
        unique=False,
        index=False,
        doc='Telegram name of user.',
    )
    timezone: orm.Mapped[float] = sa.Column(  # type: ignore
        'timezone',
        sa.Float,
        nullable=False,
        unique=False,
        index=False,
        default=3,
        server_default='3',
        doc='Timezone of user. (e.g. 3, -11, 5.5)',
    )

    def __repr__(self):  # type: ignore
        return f'<User {self.tg_id}>'
