from datetime import datetime
from app.db.models import Notification
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def create_notification(
    session: AsyncSession,
    telegram_id: int,
    notification_text: str,
    event_time_utc: datetime,
    notification_advance_time: int,
):
    notification = Notification(
        telegram_id=telegram_id,
        notification_text=notification_text,
        event_time_utc=event_time_utc,
        notification_advance_time=notification_advance_time,
    )
    session.add(notification)
    await session.commit()


async def get_all_unsent_notifications(
    session: AsyncSession, telegram_id: int
) -> tuple[Notification, ...]:
    query = (
        select(Notification)
        .where(Notification.telegram_id == telegram_id)
        .where(Notification.is_sent.is_(False))
    )
    return tuple(await session.scalars(query))
