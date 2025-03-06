import asyncio
import logging

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from telegram_bot.activity import user_last_activity, user_sessions
from telegram_bot.services.borrowing import get_borrowing

router = Router()


@router.message(Command("borrowings"))
async def cmd_me(message: types.Message, state: FSMContext):
    await message.answer("⏳ Waiting for fetching your borrowing information...")

    telegram_id = message.from_user.id
    user_last_activity[telegram_id] = asyncio.get_event_loop().time()
    user_sessions[telegram_id] = (message, None)

    logging.info(f"User {telegram_id} has started 'borrowing' handling.")
    logging.info(
        f"Updated user activity: {telegram_id} -> {user_last_activity[telegram_id]}"
    )
    logging.info(f"Current user activity dictionary: {user_last_activity}")

    user_data = await state.get_data()
    email = user_data.get("email")

    if not email:
        await message.answer(
            "⚠️ You are not authorized. Please log in using the /login command."
        )
        return

    try:
        borrowings = await get_borrowing(telegram_id)

        if borrowings:
            borrowing_list = ""

            for borrowing in borrowings:
                borrowing_list += (
                    f"📚 <b>Book:</b> {borrowing['book_title']}\n"
                    f"✍️ <b>Authors:</b> {borrowing['authors']}\n"
                    f"👀 <b>Status:</b> {borrowing['status']}\n"
                    f"🕔 <b>Borrowed:</b> {borrowing['borrow_date']}\n"
                    f"🕧 <b>Expected return date:</b> {borrowing['expected_return_date']}\n"
                    f"🕐 <b>Actual return date:</b> {borrowing['actual_return_date']}\n"
                    f"---------------\n"
                )

            await message.answer(
                f"Here is your borrowing history:\n\n{borrowing_list}",
                parse_mode="HTML",
            )
        else:
            await message.answer(
                "You still don't have any borrowings. Let`s change this!"
            )

    except Exception as e:
        logging.error(f"Error fetching borrowings: {e}", exc_info=True)
        await message.answer(
            "🚨 An error occurred while fetching your borrowings. Please try again later."
        )
