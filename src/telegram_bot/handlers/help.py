import asyncio
import logging

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import FSInputFile

from telegram_bot.activity import user_last_activity, user_sessions

router = Router()


@router.message(Command("help"))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    user_last_activity[user_id] = asyncio.get_event_loop().time()
    user_sessions[user_id] = (message, None)

    logging.info(f"User {user_id} initialized help action")
    logging.info(f"Updated user activity: {user_id} -> {user_last_activity[user_id]}")
    logging.info(f"Current user activity dictionary: {user_last_activity}")

    photo_path = "telegram_bot/media/cat-busy.gif"
    photo = FSInputFile(photo_path)

    await message.answer_photo(
        photo,
        caption="Hello! Here is list of available commands:\n\n"
        "/start - Start a session\n"
        "/help - Display help\n"
        "/login - Login to your library account\n"
        "/books - Display list of available books\n"
        "/me - Display information about yourself\n"
        "/borrowings - Display your borrowings\n"
        "/stop - Stop session\n",
    )
