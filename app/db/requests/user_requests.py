from sqlalchemy.ext.asyncio import AsyncSession
from app.db import User


async def create_user(
    session: AsyncSession,
    telegram_id: int,
    user_timezone_offset: int | None = None,
):
    if not await get_user_by_telegram_id(session=session, telegram_id=telegram_id):
        user = User(telegram_id=telegram_id, user_timezone_offset=user_timezone_offset)
        session.add(user)
        await session.commit()


async def get_user_by_telegram_id(
    session: AsyncSession, telegram_id: int
) -> User | None:
    user = await session.get(User, telegram_id)
    return user


async def update_user(
    session: AsyncSession, telegram_id: int, user_timezone_offset: int | None = None
):
    if user := await session.get(User, telegram_id):
        user.user_timezone_offset = (
            user_timezone_offset
            if user_timezone_offset is not None
            else user.user_timezone_offset
        )
    await session.commit()
