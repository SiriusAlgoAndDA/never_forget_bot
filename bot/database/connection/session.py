import functools
import typing as tp
from contextlib import asynccontextmanager, contextmanager

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from bot import config


class SessionManager:  # pragma: no cover
    """
    A class that implements the necessary
    functionality for working with the database:
    issuing sessions, storing and updating connection settings.
    """

    ENGINE_KWARGS = {
        'max_overflow': 16,
        'pool_size': 32,
        'pool_timeout': 60,
    }

    def __new__(cls) -> 'SessionManager':
        if not hasattr(cls, 'instance'):
            cls.instance = super(SessionManager, cls).__new__(cls)
            cls.instance.engine = None  # type: ignore
            cls.instance.async_engine = None  # type: ignore
            cls.instance._create_engines()  # type: ignore
        return cls.instance  # noqa

    def get_session_maker(self) -> sessionmaker:  # type: ignore
        return sessionmaker(bind=self.engine)  # type: ignore

    def get_async_session_maker(self) -> async_sessionmaker:  # type: ignore
        return async_sessionmaker(self.async_engine, expire_on_commit=False)  # type: ignore  # noqa: E501

    def _create_engines(self) -> None:
        settings = config.get_settings()
        self.engine = sa.create_engine(
            settings.database_uri_sync,
            **self.ENGINE_KWARGS,
        )
        self.async_engine = create_async_engine(
            settings.database_uri,
            echo=True,
            future=True,
            pool_pre_ping=True,
            **self.ENGINE_KWARGS,
        )

    async def refresh(self) -> None:
        if self.engine:  # type: ignore
            self.engine.dispose()  # type: ignore
        if self.async_engine:  # type: ignore
            await self.async_engine.dispose()  # type: ignore
        self._create_engines()

    @contextmanager
    def create_session(self, **kwargs: tp.Any) -> tp.Generator[Session, None, None]:
        with self.get_session_maker()(**kwargs) as new_session:
            try:
                yield new_session
                new_session.commit()
            except Exception:
                new_session.rollback()
                raise
            finally:
                new_session.close()

    @asynccontextmanager
    async def create_async_session(self, **kwargs: tp.Any) -> tp.AsyncGenerator[AsyncSession, None]:
        async with self.get_async_session_maker()(**kwargs) as new_session:
            try:
                yield new_session
                await new_session.commit()
            except Exception:
                await new_session.rollback()
                raise
            finally:
                await new_session.close()

    async def get_async_session(self) -> tp.AsyncGenerator[AsyncSession, None]:
        async with self.create_async_session(expire_on_commit=False) as session:
            yield session

    def with_session(self, func: tp.Callable) -> tp.Callable:  # type: ignore
        @functools.wraps(func)
        async def wrapper(*args: tp.Any, **kwargs: tp.Any) -> tp.Any:
            async with self.create_async_session() as session:
                return await func(*args, session=session, **kwargs)

        return wrapper
