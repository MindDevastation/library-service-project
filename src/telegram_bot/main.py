import asyncio
import logging
import os
import sys
import django

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library.settings")

django.setup()

from aiogram import Bot, Dispatcher, Router

from config import BOT_TOKEN
from handlers import start, token, stop, auth, books


logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

# Connecting handlers
dp.include_router(start.router)
dp.include_router(token.router)
dp.include_router(stop.router)
dp.include_router(auth.router)
dp.include_router(books.router)


async def on_start():
    logging.info("Starting bot...")


async def on_shutdown():
    logging.warning("Shutting down...")
    await bot.close()


async def main():
    print("Bot is on!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
