from aiogram import types, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from telegram_bot.services.db import disconnect_db

router = Router()


@router.message(Command("stop"))
async def stop(message: types.Message, state: FSMContext):
    await state.clear()
    await disconnect_db()

    await message.answer(
        "🚫 Your session has been terminated.\n"
        "To start again, use the /start command.",
        parse_mode=ParseMode.MARKDOWN,
    )
