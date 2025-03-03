from aiogram import types, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command

from aiogram.fsm.context import FSMContext

router = Router()


@router.message(Command("stop"))
async def stop(message: types.Message, state: FSMContext):
    await cmd_stop(message, state)


# This handler will terminate the user's session
async def cmd_stop(message: types.Message, state: FSMContext):
    # Clear user state
    await state.finish()

    chat_id = message.chat.id
    user_messages = await message.bot.get_chat(chat_id)

    await message.delete()
    await state.finish()

    # Send a message that the session is complete
    await message.answer(
        "Your session is over. You can start again with the /start command.",
        parse_mode=ParseMode.MARKDOWN,
    )
