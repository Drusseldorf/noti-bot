import asyncio
from datetime import datetime, UTC
from sqlalchemy import select, text
from sqlalchemy.orm import joinedload

from app.db.models import Notification
from app.db.db_session import db_helper
from app.helpers.datetime_helpers import to_user_time
from app.tg_bot import bot
from app.tg_bot.ru_text.ru_text import ru_message
from config_data.config import settings


notification_check_interval_seconds = settings.notification_check_interval_seconds


async def check_reminders():
    async with db_helper.session_factory() as session:
        query = (
            select(Notification)
            .options(joinedload(Notification.user))
            .where(
                (
                    Notification.event_time_utc
                    - text("INTERVAL '1 minute' * notification_advance_time")
                )
                <= datetime.now(UTC).replace(tzinfo=None)
            )
            .where(Notification.is_sent.is_(False))
        )

        notifications = await session.scalars(query)

        for notification in notifications.unique():
            await send_notifications(notification)
            notification.is_sent = True
            session.add(notification)
            await session.commit()


async def send_notifications(notification):
    await bot.send_message(
        chat_id=notification.telegram_id,
        text=ru_message.reminder_message.format(
            notification.notification_text,
            to_user_time(
                notification.event_time_utc,
                notification.user.user_timezone_offset,
            ),
        ),
    )


async def reminder_scheduler():
    while True:
        await check_reminders()
        await asyncio.sleep(notification_check_interval_seconds)
