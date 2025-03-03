# from asgiref.sync import sync_to_async
# from books.models import Book
#
# @sync_to_async
# def get_books_sync():
#     return Book.objects.all()
#
# async def get_books():
#     books = await get_books_sync()
#     return books

from telegram_bot.services.db import database


async def get_books():
    query = """
    SELECT 
        book.title AS book_title,
        STRING_AGG(author.name, ', ') AS authors
    FROM 
        books_book book
    JOIN 
        books_book_authors ba ON book.id = ba.book_id
    JOIN 
        books_author author ON ba.author_id = author.id
    GROUP BY 
        book.title;
    """
    rows = await database.fetch_all(query)
    return rows
