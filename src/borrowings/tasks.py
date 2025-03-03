from celery import shared_task
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings
from .models import Borrowing
import requests


@shared_task
def check_overdue_borrowings():
    today = now().date()
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=today,
        actual_return_date__isnull=True,
        status=Borrowing.Status.PENDING,
    )

    if not overdue_borrowings.exists():
        send_telegram_notification("No borrowings overdue today!")
        return

    for borrowing in overdue_borrowings:
        message = (
            f"Overdue Borrowing Alert:\n"
            f"Book: {borrowing.book.title}\n"
            f"User: {borrowing.user.email}\n"
            f"Expected Return Date: {borrowing.expected_return_date}\n"
            f"Status: {borrowing.status}"
        )
        send_telegram_notification(message)


def send_telegram_notification(message):
    """
    Sends a message to a Telegram chat.
    Replace 'YOUR_TELEGRAM_BOT_TOKEN' and 'YOUR_CHAT_ID' with actual values.
    """
    bot_token = "YOUR_TELEGRAM_BOT_TOKEN"
    chat_id = "YOUR_CHAT_ID"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=payload)
    return response.json()
