import asyncio
from sqlalchemy import func, text
from sqlalchemy.future import select
from app.db.models import User, Notification
from app.db.db_session import db_helper
from app.tg_bot import bot
from config_data.config import settings


notification_check_interval_seconds = settings.notification_check_interval_seconds


async def check_reminders():
    async with db_helper.session_factory() as session:
        now_utc = func.now().op("AT TIME ZONE")("UTC")
        minute_interval = text("INTERVAL '1 minute'")
        query = (
            select(Notification)
            .join(User, User.telegram_id == Notification.telegram_id)
            .where(
                Notification.is_sent.is_(False),
                now_utc + (User.minutes_before_noti * minute_interval)
                >= Notification.event_time,  # а юзер то пишет время напоминания тоже в своем поясе!!!
            )
        )
        notifications = await session.scalars(query)
        for notification in notifications.unique():
            await bot.send_message(
                chat_id=notification.telegram_id,
                text=f"Время: {notification.time_to_notify}\nНапоминание: {notification.notification_text}",
            )
            notification.is_sent = True
            session.add(notification)
            await session.commit()


async def reminder_scheduler():
    while True:
        await check_reminders()
        await asyncio.sleep(notification_check_interval_seconds)
