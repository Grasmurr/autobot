from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from telegram_bot.assets import config

bot = Bot(token=config.API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
