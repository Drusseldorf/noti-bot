from aiogram import Dispatcher, Bot
from app.tg_bot.handlers.fsm_get_notification import fsm_router
from config_data.config import settings
from app.tg_bot.handlers.commands import commands_router

bot = Bot(token=settings.bot_token)

dp = Dispatcher()

dp.include_router(commands_router)
dp.include_router(fsm_router)
