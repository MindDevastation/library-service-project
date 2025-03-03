from books.models import Book

from celery import shared_task


@shared_task
def count_books():
    return Book.objects.count()
