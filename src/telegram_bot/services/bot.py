from aiogram import Bot

from telegram_bot.config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)


async def send_borrowing_notification(borrowing):
    user = borrowing.user
    message = (
        f"Hello, {user.first_name}!\n"
        f"Your borrowing request for the book '{borrowing.book.title}' has been processed.\n"
        f"Expected return date: {borrowing.expected_return_date}\n"
        f"Status: {borrowing.status}\n"
    )
    try:
        # Sending a message to a user via Telegram ID
        await bot.send_message(user.telegram_id, message)
    except Exception as e:
        print(f"Error sending message: {e}")
