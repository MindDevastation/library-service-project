from aiogram import types
from aiogram.filters import Command
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from telegram_bot.services.auth import login_user

router = Router()


class AuthState(StatesGroup):
    waiting_for_email = State()
    waiting_for_password = State()
    authenticated = State()


@router.message(Command("login"))
async def cmd_login(message: types.Message, state: FSMContext):
    await message.answer("Please enter your email to log in.")
    await state.set_state(AuthState.waiting_for_email)


@router.message(AuthState.waiting_for_email)
async def handle_email(message: types.Message, state: FSMContext):
    email = message.text.strip()
    await state.update_data(email=email)
    await message.answer("Now enter your password.")
    await state.set_state(AuthState.waiting_for_password)


@router.message(AuthState.waiting_for_password)
async def handle_password(message: types.Message, state: FSMContext):
    password = message.text.strip()
    user_data = await state.get_data()
    email = user_data.get("email")

    if login_user(email, password):
        await message.answer(
            "You've successfully logged in! You now have access to the books."
        )
        await state.set_state(AuthState.authenticated)
    else:
        await message.answer("Invalid email or password. Try again.")
        await state.finish()
