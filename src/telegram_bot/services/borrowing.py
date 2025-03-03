from telegram_bot.services.db import database


async def get_borrowing(telegram_id):
    query = (
        f"SELECT borrowing.*, bk.title AS book_title, STRING_AGG(a.name, ',') AS authors "
        f"FROM borrowings_borrowing borrowing "
        f"JOIN users_user users ON borrowing.user_id = users.id "
        f"JOIN books_book_authors ba ON ba.book_id = borrowing.book_id "
        f"JOIN books_author a ON ba.author_id = a.id "
        f"JOIN books_book bk ON borrowing.book_id = bk.id "
        f"WHERE users.telegram_id = {telegram_id} "
        f"GROUP BY borrowing.id, book_title; "
    )
    rows = await database.fetch_all(query)
    return rows
