import asyncio
from app.tg_bot import bot, dp


async def main():
    polling_task = asyncio.create_task(dp.start_polling(bot))
    # reminders_task = asyncio.create_task(reminder_scheduler())

    await asyncio.gather(polling_task)


if __name__ == "__main__":
    asyncio.run(main())
