import asyncio
import logging

from aiogram import types
from aiogram.filters import Command
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from telegram_bot.activity import user_last_activity, user_sessions
from telegram_bot.services.auth import login_user
from telegram_bot.services.db import database


router = Router()


class AuthState(StatesGroup):
    waiting_for_email = State()
    waiting_for_password = State()
    authenticated = State()


@router.message(Command("login"))
async def cmd_login(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    await message.answer("⏳ Authorizing...")
    user_id = message.from_user.id
    user_last_activity[user_id] = asyncio.get_event_loop().time()
    user_sessions[user_id] = (message, None)

    logging.info(f"User {user_id} started login")
    logging.info(f"Updated user activity: {user_id} -> {user_last_activity[user_id]}")
    logging.info(f"Current user activity dictionary: {user_last_activity}")

    if database.is_connected:
        # Check if there is a user with this telegram_id
        query = "SELECT email FROM users_user WHERE telegram_id = :telegram_id"
        user = await database.fetch_one(query, {"telegram_id": telegram_id})

        if user:
            await state.update_data(email=user["email"])
            await message.answer("✅ You are already logged in! Welcome back!")
            await state.set_state(AuthState.authenticated)
        else:
            await message.answer("🔑 Please enter your email to log in.")
            await state.set_state(AuthState.waiting_for_email)
    else:
        await message.answer(
            "You still not started. Please write /start to get started."
        )


@router.message(AuthState.waiting_for_email)
async def handle_email(message: types.Message, state: FSMContext):
    email = message.text.strip()
    await state.update_data(email=email)
    await message.answer("🔒 Now enter your password.")
    await state.set_state(AuthState.waiting_for_password)
    user_id = message.from_user.id
    user_last_activity[user_id] = asyncio.get_event_loop().time()
    user_sessions[user_id] = (message, None)

    logging.info(f"User {user_id} entered email: {email}")
    logging.info(f"Updated user activity: {user_id} -> {user_last_activity[user_id]}")
    logging.info(f"Current user activity dictionary: {user_last_activity}")


@router.message(AuthState.waiting_for_password)
async def handle_password(message: types.Message, state: FSMContext):
    password = message.text.strip()
    user_data = await state.get_data()
    email = user_data.get("email")
    telegram_id = message.from_user.id

    if login_user(email, password):
        # After successful login, we immediately write telegram_id
        update_query = """
                            UPDATE users_user 
                            SET telegram_id = :telegram_id 
                            WHERE email = :email
                            """
        await database.execute(
            update_query, {"telegram_id": telegram_id, "email": email}
        )

        await message.answer(
            "✅ You've successfully logged in! You now have access to the books."
        )
        await state.set_state(AuthState.authenticated)
    else:
        await message.answer("❌ Invalid email or password. Try again.")
        await state.finish()
    user_id = message.from_user.id
    user_last_activity[user_id] = asyncio.get_event_loop().time()
    user_sessions[user_id] = (message, None)

    logging.info(f"User {user_id} entered password: {password}")
    logging.info(f"User created. Telegram ID: {telegram_id} -> {user_id}")
    logging.info(f"Updated user activity: {user_id} -> {user_last_activity[user_id]}")
    logging.info(f"Current user activity dictionary: {user_last_activity}")
