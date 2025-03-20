import os

import asyncio
import logging

from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile

from telegram_bot.activity import user_last_activity, user_sessions
from telegram_bot.services.db import connect_db

router = Router()


@router.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer("⏳ Starting. Please wait a while...")

    try:
        await connect_db()
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        await message.answer(
            "⚠️ Failed to connect to the database. Please try again later."
        )
        return

    telegram_id = message.from_user.id
    user_last_activity[telegram_id] = asyncio.get_event_loop().time()
    user_sessions[telegram_id] = (message, None)

    logging.info(
        f"Updated user activity: {telegram_id} -> {user_last_activity[telegram_id]}"
    )
    logging.info(f"Current user activity dictionary: {user_last_activity}")
    logging.info(
        f"Created session for user {telegram_id}: {user_sessions[telegram_id]}"
    )

    photo_path = "telegram_bot/media/library.jpg"

    if os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(
            photo,
            caption="Hi! I'm a library bot.📚 Authorize using /login to get started.\n"
            "Type /help to navigate through the library.",
        )
    else:
        logging.error(f"Start image not found: {photo_path}")
        await message.answer(
            "Hi! I'm a library bot.📚 Authorize using /login to get started.\n"
            "Type /help to navigate through the library."
        )
