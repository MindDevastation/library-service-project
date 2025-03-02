from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from borrowings.models import Borrowing


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
