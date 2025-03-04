import logging
from datetime import datetime

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from books.models import Book
from borrowings.models import Borrowing
from logging_app.models import ActionLog
from payments.models import StripePayment, PayPalPayment

logger = logging.getLogger("user_actions")


@receiver(post_save, sender=Book)
def log_book_changes(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"{timestamp} - Book (ID: {instance.id}) {instance.title} was {action}")
    ActionLog.objects.create(action=action, model_name="Book", object_id=instance.id)


@receiver(post_delete, sender=Book)
def log_book_deletion(sender, instance, **kwargs):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"{timestamp} - Book (ID: {instance.id}) {instance.title} was deleted")
    ActionLog.objects.create(action="deleted", model_name="Book", object_id=instance.id)


@receiver(post_save, sender=Borrowing)
def log_borrowing_changes(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(
        f"{timestamp} - User {instance.user} {action} Borrowing (ID: {instance.id})"
    )
    ActionLog.objects.create(
        user=instance.user, action=action, model_name="Borrowing", object_id=instance.id
    )


@receiver(post_delete, sender=Borrowing)
def log_borrowing_deletion(sender, instance, **kwargs):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(
        f"{timestamp} - User {instance.user} deleted Borrowing (ID: {instance.id})"
    )
    ActionLog.objects.create(
        user=instance.user,
        action="deleted",
        model_name="Borrowing",
        object_id=instance.id,
    )


@receiver(post_save, sender=StripePayment)
def log_stripe_payment_changes(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"{timestamp} - Stripe Payment №{instance.id} {action}")
    ActionLog.objects.create(
        action=action, model_name="StripePayment", object_id=instance.id
    )


@receiver(post_delete, sender=StripePayment)
def log_stripe_payment_deletion(sender, instance, **kwargs):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"{timestamp} - Stripe Payment №{instance.id} deleted")
    ActionLog.objects.create(
        action="deleted", model_name="StripePayment", object_id=instance.id
    )


@receiver(post_save, sender=PayPalPayment)
def log_paypal_payment_changes(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"{timestamp} - PayPal Payment №{instance.id} {action}")
    ActionLog.objects.create(
        action=action, model_name="PayPalPayment", object_id=instance.id
    )


@receiver(post_delete, sender=PayPalPayment)
def log_paypal_payment_deletion(sender, instance, **kwargs):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"{timestamp} - PayPal Payment №{instance.id} deleted")
    ActionLog.objects.create(
        action="deleted", model_name="PayPalPayment", object_id=instance.id
    )
