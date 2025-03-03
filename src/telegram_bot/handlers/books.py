# telegram_bot/handlers/books.py

from aiogram import types
from aiogram.filters import Command
from aiogram import Router
from aiogram.fsm.context import FSMContext
from telegram_bot.services.books import (
    get_books,
)  # Function for obtaining the list of books
from telegram_bot.services.db import (
    connect_db,
    disconnect_db,
)  # Functions for connecting and disconnecting the database

router = Router()


@router.message(Command("books"))
async def cmd_books(message: types.Message, state: FSMContext):
    await message.answer("⏳ Waiting for books...")
    # Connecting to the database
    await connect_db()

    try:
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
                book_list += f"{book['book_id']} - {book['book_title']} ({book['authors']}). Daily fee {book['daily_fee']}$\n"

            await message.answer(f"Here's a list of available books:\n{book_list}")
        else:
            await message.answer("No books found.")
    finally:
        await disconnect_db()
