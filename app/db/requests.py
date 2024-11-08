from datetime import datetime
from app.db.models import Notification
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import User
from sqlalchemy.exc import IntegrityError


async def create_user_if_not_exist(session: AsyncSession, telegram_id: int):
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        user = User(telegram_id=telegram_id)
        session.add(user)
        await session.commit()


async def get_user_by_telegram_id(
    session: AsyncSession, telegram_id: int
) -> User | None:
    stmt = select(User).where(User.telegram_id == telegram_id)
    user = await session.scalar(stmt)
    return user


# TODO: обрабатывать исключения нужно на функциях, которые вызывают эту, а не тут
async def create_notification(
    session: AsyncSession,
    telegram_id: int,
    notification_text: str,
    time_to_notify: datetime,
):
    notification = Notification(
        telegram_id=telegram_id,
        notification_text=notification_text,
        time_to_notify=time_to_notify,
    )
    try:
        session.add(notification)
        await session.commit()
        await session.close()
        result = notification
    except IntegrityError:
        result = False
    return result


async def get_all_notifications(session: AsyncSession, telegram_id: int):
    stmt = select(Notification).where(Notification.telegram_id == telegram_id)
    notification_scalars = await session.scalars(stmt)
    return [
        (noti.notification_text, noti.time_to_notify)
        for noti in notification_scalars.unique()
    ]
