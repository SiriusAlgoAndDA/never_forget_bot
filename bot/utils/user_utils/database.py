from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import models


async def get_user(session: AsyncSession, tg_id: str) -> models.User | None:
    query = select(models.User).where(models.User.tg_id == tg_id)
    return await session.scalar(query)


async def add_user(session: AsyncSession, tg_id: str, tg_username: str, tg_name: str) -> models.User:
    user = models.User(tg_id=tg_id, tg_username=tg_username, tg_name=tg_name)
    session.add(user)
    await session.commit()
    return user


async def change_timezone(session: AsyncSession, tg_id: str, new_timezone: float) -> None:
    query = update(models.User).where(models.User.tg_id == tg_id).values(timezone=new_timezone)
    await session.execute(query)
