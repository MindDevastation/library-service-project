import asyncio
import logging

from aiogram import types
from aiogram.filters import Command
from aiogram import Router
from aiogram.fsm.context import FSMContext

from telegram_bot.activity import user_last_activity, user_sessions
from telegram_bot.services.books import (
    get_books,
)  # Function for obtaining the list of books

router = Router()


@router.message(Command("books"))
async def cmd_books(message: types.Message, state: FSMContext):
    await message.answer("⏳ Waiting for books...")
    telegram_id = message.from_user.id
    user_last_activity[telegram_id] = asyncio.get_event_loop().time()
    user_sessions[telegram_id] = (message, None)

    logging.info(f"User {telegram_id} has started 'book' handling.")
    logging.info(
        f"Updated user activity: {telegram_id} -> {user_last_activity[telegram_id]}"
    )
    logging.info(f"Current user activity dictionary: {user_last_activity}")

    # Check if the user is logged in
    user_data = await state.get_data()
    email = user_data.get("email")  # Assume that email is stored after login

    if not email:
        await message.answer(
            "⚠️ You are not authorized. Please log in using the /login command."
        )
        return

    # Get a list of books
    books = await get_books()

    if books:
        # Form a line with book titles and their authors
        book_list = ""
        for book in books:
            book_list += (
                f"{book['book_id']} - {book['book_title']} "
                f"({book['authors']}). Daily fee <b>{book['daily_fee']}$</b>\n"
            )

        await message.answer(
            f"✍️ Here's a list of available books:\n{book_list}", parse_mode="HTML"
        )
    else:
        await message.answer("🗿 No books found.")
