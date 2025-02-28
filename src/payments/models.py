from uuid import uuid4

import stripe
from django.conf import settings
from django.db import models

from borrowings.models import Borrowing


class Payment(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Is in the process"
        PAID = "PAID", "Successfully paid"
        FAILED = "FAILED", "Payment failed"
        CANCELED = "CANCELED", "Payment canceled"
        REFUNDED = "REFUNDED", "Payment refunded"

    class Type(models.TextChoices):
        PAYMENT = "PAYMENT", "Common payment"
        FINE = "FINE", "Penalty"

    class Currency(models.TextChoices):
        USD = "USD", "US Dollar"
        EUR = "EUR", "Euro"

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    type = models.CharField(max_length=10, choices=Type.choices, default=Type.PAYMENT)
    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(max_digits=5, decimal_places=2, positive=True)
    borrow_date = models.DateField()
    payment_id = models.UUIDField(default=uuid4, editable=False, unique=True)
    currency = models.CharField(
        max_length=3, choices=Currency.choices, default=Currency.USD, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["borrowing"]),
        ]
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self.borrowing:
            self.borrow_date = self.borrowing.borrow_date
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.type} payment of {self.amount} on {self.borrow_date}"


class StripePayment(Payment):
    payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    objects = models.Manager()

    def create_payment_intent(self):
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY

            payment_intent = stripe.PaymentIntent.create(
                amount=int(self.amount * 100),
                currency=self.currency.lower(),
                metadata={"borrow_id": self.borrowing.id},
            )
            self.payment_intent_id = payment_intent["id"]
            self.save()
            return payment_intent
        except stripe.error.StripeError as error:
            raise ValueError(f"Stripe error occurred: {error.user_message}")
