import asyncio
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from payments.models import Payment
from telegram_bot.services.bot import send_payment_notification

logger = logging.getLogger("borrowing_payment_user_actions")


# Asynchronous wrapper for calling send_payment_notification
async def send_notification_payment_async(instance):
    try:
        # Sending a notification
        await send_payment_notification(instance)
        logger.info(
            f"📚 Payment created: '{instance.book.title}' for user {instance.user.email}. Notification sent."
        )
    except Exception as e:
        logger.error(f"❌ Error sending payment notification: {str(e)}")


@receiver(post_save, sender=Payment)
def send_payment_notification_to_user(sender, instance, created, **kwargs):
    if created:
        # Check for telegram_id
        telegram_id = instance.user.telegram_id
        if telegram_id:
            try:
                # Create a new event loop if it does not exist in the current thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                # Starting an asynchronous task
                loop.run_until_complete(send_notification_payment_async(instance))
            except Exception as e:
                logger.error(
                    f"❌ Error in creating event loop or sending notification: {str(e)}"
                )
            finally:
                loop.close()  # Close the event loop after completion
        else:
            logger.warning(
                f"⚠️ Payment created: '{instance.book.title}' for user {instance.user.email}, but no telegram_id found."
            )
