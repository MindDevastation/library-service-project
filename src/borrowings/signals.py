import asyncio
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from borrowings.models import Borrowing
from telegram_bot.services.bot import send_borrowing_notification
from users.models import User

logger = logging.getLogger("borrowing_user_actions")


@receiver(post_save, sender=User)
def send_registration_email(sender, instance, created, **kwargs):
    if created:
        print("Sending registration email")

        subject = "Welcome to Our Service!"
        html_message = render_to_string(
            "registration_success_email.html", {"user": instance}
        )
        plain_message = strip_tags(html_message)
        from_email = "no-reply@yourdomain.com"
        to_email = instance.email

        send_mail(
            subject,
            plain_message,
            from_email,
            [to_email],
            html_message=html_message,
            fail_silently=False,
        )


@receiver(post_save, sender=Borrowing)
def send_borrowing_confirmation_email(sender, instance, created, **kwargs):
    if created:
        subject = f"Borrowing #{instance.id} Confirmation"
        html_message = render_to_string(
            "borrowing_confirmation_email.html", {"borrowing": instance}
        )
        plain_message = strip_tags(html_message)
        from_email = "no-reply@yourdomain.com"
        to_email = instance.user.email

        send_mail(
            subject,
            plain_message,
            from_email,
            [to_email],
            html_message=html_message,
            fail_silently=True,
        )


@receiver(post_save, sender=Borrowing)
def send_borrowing_status_update(sender, instance, **kwargs):
    if instance.status in [Borrowing.Status.RETURNED, Borrowing.Status.OVERDUE]:
        user = instance.user
        if user:
            print(f"Borrowing status updated to: {instance.status}")

            subject = f"Borrowing {instance.id} Status Update"
            html_message = render_to_string(
                "borrowing_status_update_email.html", {"borrowing": instance}
            )
            plain_message = strip_tags(html_message)
            from_email = "no-reply@yourdomain.com"
            to_email = instance.user.email

            send_mail(
                subject,
                plain_message,
                from_email,
                [to_email],
                html_message=html_message,
                fail_silently=True,
            )


# Asynchronous wrapper for calling send_borrowing_notification
async def send_notification_async(instance):
    try:
        # Отправка уведомления
        await send_borrowing_notification(instance)
        logger.info(
            f"📚 Borrowing created: '{instance.book.title}' for user {instance.user.email}. Notification sent."
        )
    except Exception as e:
        logger.error(f"❌ Error sending borrowing notification: {str(e)}")


@receiver(post_save, sender=Borrowing)
def send_borrowing_notification_to_user(sender, instance, created, **kwargs):
    if created:
        # Check for telegram_id
        telegram_id = instance.user.telegram_id
        if telegram_id:
            try:
                # Create a new event loop if it does not exist in the current thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                # Starting an asynchronous task
                loop.run_until_complete(send_notification_async(instance))
            except Exception as e:
                logger.error(
                    f"❌ Error in creating event loop or sending notification: {str(e)}"
                )
            finally:
                loop.close()  # Close the event loop after completion
        else:
            logger.warning(
                f"⚠️ Borrowing created: '{instance.book.title}' for user {instance.user.email}, but no telegram_id found."
            )
