import asyncio
import logging

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from telegram_bot.activity import user_last_activity, user_sessions
from telegram_bot.services.me import get_me

router = Router()


@router.message(Command("me"))
async def cmd_me(message: types.Message, state: FSMContext):
    await message.answer("⏳ Waiting for fetching your profile information...")

    user_id = message.from_user.id
    user_last_activity[user_id] = asyncio.get_event_loop().time()
    user_sessions[user_id] = (message, None)

    logging.info(f"User {user_id} has started 'me' handling.")
    logging.info(f"Updated user activity: {user_id} -> {user_last_activity[user_id]}")
    logging.info(f"Current user activity dictionary: {user_last_activity}")

    user_data = await state.get_data()
    email = user_data.get("email")

    if not email:
        await message.answer(
            "⚠️ You are not authorized. Please log in using the /login command."
        )
        return

    me = await get_me(user_id)

    info = ""
    info += (
        f"Name: {me['first_name']} {me['last_name']}\n"
        f"Email: {me['email']}\n"
        f"Joined on: {me['date_joined']}\n"
        f"Last login: {me['last_login']}\n\n"
        f"To navigate through library type /help"
    )

    await message.answer(f"Here is your profile information:\n\n{info}")
