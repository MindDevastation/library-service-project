import asyncio
import logging

from aiogram import Router, types
from aiogram.filters import CommandStart

from telegram_bot.activity import user_last_activity, user_sessions
from telegram_bot.services.db import connect_db

router = Router()


@router.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer("⏳ Starting. Please wait a while...")
    await connect_db()
    user_id = message.from_user.id
    user_last_activity[user_id] = asyncio.get_event_loop().time()
    user_sessions[user_id] = (message, None)

    logging.info(f"Updated user activity: {user_id} -> {user_last_activity[user_id]}")
    logging.info(f"Current user activity dictionary: {user_last_activity}")
    logging.info(f"Created session for user {user_id}: {user_sessions[user_id]}")

    await message.answer(
        "Hi! I'm a library bot.📚 Authorize using /login to get started."
    )
