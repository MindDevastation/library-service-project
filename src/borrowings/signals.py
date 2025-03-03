import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from borrowings.models import Borrowing
from telegram_bot.services.bot import send_borrowing_notification
from users.models import User

logger = logging.getLogger(__name__)


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


@receiver(post_save, sender=Borrowing)
def send_borrowing_notification_to_user(sender, instance, created, **kwargs):
    if created:
        try:
            # Get user's telegram_id
            telegram_id = instance.user.telegram_id
            if telegram_id:
                # Sending a message via Telegram
                send_borrowing_notification(instance)
                logger.info(
                    f"Sent borrowing notification for user {instance.user.email}."
                )
            else:
                logger.warning(
                    f"User {instance.user.email} does not have a telegram_id."
                )
        except Exception as e:
            logger.error(f"Error sending borrowing notification: {str(e)}")
