import os
import sys

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from telegram_bot.services.token import login_user

router = Router()


class AuthState(StatesGroup):
    waiting_for_email_token = State()
    waiting_for_password_token = State()


# The /token command starts the authorization process
@router.message(Command("token"))
async def get_token(message: types.Message, state: FSMContext):
    await message.answer("Enter your email:")
    await state.set_state(AuthState.waiting_for_email_token)


# Processing email input
@router.message(AuthState.waiting_for_email_token, F.text)
async def process_email(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("Enter your password:")
    await state.set_state(AuthState.waiting_for_password_token)


# Process the password input and try to authorize the user
@router.message(AuthState.waiting_for_password_token, F.text)
async def process_password(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    email = user_data["email"]
    password = message.text

    auth_response = await login_user(email, password)
    if auth_response:
        token = auth_response.get("access")  # Getting an access token
        refresh_token = auth_response.get("refresh")  # Getting a refresh token
        await message.answer(f"Successful authorization! Your access token: {token}")
        # This is where you can save access and refresh tokens in the database or in Redis for later use
    else:
        await message.answer("Authorization Error. Check email and password.")

    await state.clear()
