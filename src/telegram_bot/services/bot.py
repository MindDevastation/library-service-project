from aiogram import Bot

from telegram_bot.config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)


async def send_borrowing_notification(borrowing):
    user = borrowing.user
    book = borrowing.book
    difference = borrowing.expected_return_date - borrowing.borrow_date
    message = (
        f"Hello, {user.first_name}!\n"
        f"Your borrowing request for the book '{book.title}' has been processed.\n"
        f"Expected return date: {borrowing.expected_return_date}\n"
        f"Status: {borrowing.status}\n"
        f"You took this book for {difference.days + 1} days.\n"
        f"Expected money to pay: {(difference.days + 1) * book.daily_fee}\n"
    )
    try:
        # Sending a message to a user via Telegram ID
        await bot.send_message(user.telegram_id, message)
    except Exception as e:
        print(f"Error sending message: {e}")


async def send_payment_notification(payment):
    user = payment.borrowing.user
    book = payment.borrowing.book
    message = (
        f"Hello, {user.first_name}!\n"
        f"Thanks for you`re purchase!\n"
        f"Your payment request for the book '{book.title}' has been processed.\n"
        f"Your payment status: {payment.status}\n"
        f"Payment id: {payment.payment_id}\n"
        f"Money to pay: {payment.amount}\n"
    )
    try:
        # Sending a message to a user via Telegram ID
        await bot.send_message(user.telegram_id, message)
    except Exception as e:
        print(f"Error sending message: {e}")
