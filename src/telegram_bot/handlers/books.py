# telegram_bot/handlers/books.py

from aiogram import types
from aiogram.filters import Command
from aiogram import Router
from aiogram.fsm.context import FSMContext
from telegram_bot.services.books import get_books  # Функция получения списка книг
from telegram_bot.services.db import (
    connect_db,
    disconnect_db,
)  # Функции для подключения и отключения базы данных

router = Router()


@router.message(Command("books"))
async def cmd_books(message: types.Message, state: FSMContext):
    # Подключаемся к базе данных
    await connect_db()

    try:
        # Проверяем, залогинен ли пользователь
        user_data = await state.get_data()
        email = user_data.get(
            "email"
        )  # Предполагаем, что email сохраняется после логина

        if not email:
            await message.answer(
                "You are not authorized. Please log in using the /login command."
            )
            return

        # Получаем список книг
        books = await get_books()

        if books:
            # Формируем строку с названиями книг и их авторами
            book_list = ""
            for book in books:
                book_list += f"{book['book_title']} - {book['authors']}\n"

            await message.answer(f"Here's a list of available books:\n{book_list}")
        else:
            await message.answer("No books found.")
    finally:
        await disconnect_db()
