from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import models


async def get_user(session: AsyncSession, tg_id: str) -> models.User | None:
    query = select(models.User).where(models.User.tg_id == tg_id)
    return await session.scalar(query)
