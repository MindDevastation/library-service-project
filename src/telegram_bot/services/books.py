from telegram_bot.services.db import database


async def get_books():
    query = """
    SELECT 
        book.title AS book_title,
        STRING_AGG(author.name, ', ') AS authors,
        book.id AS book_id,
        book.daily_fee
    FROM 
        books_book book
    JOIN 
        books_book_authors ba ON book.id = ba.book_id
    JOIN 
        books_author author ON ba.author_id = author.id
    GROUP BY 
        book.id
    ORDER BY 
        book.id;
    """
    rows = await database.fetch_all(query)
    return rows
