from uuid import uuid4

import paypalrestsdk
import stripe
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from paypalrestsdk.exceptions import (
    ResourceNotFound,
    ClientError,
    ServerError,
    MissingConfig,
    InvalidConfig,
)

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
    amount = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
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


class PayPalPayment(Payment):
    paypal_order_id = models.CharField(max_length=255, blank=True, null=True)
    payer_id = models.CharField(max_length=255, blank=True, null=True)
    objects = models.Manager()

    def create_order(self):
        base_url = "http://localhost:8000/api/payments/paypal/"
        try:
            paypalrestsdk.configure(
                {
                    "mode": settings.PAYPAL_MODE,
                    "client_id": settings.PAYPAL_CLIENT_ID,
                    "client_secret": settings.PAYPAL_SECRET,
                }
            )

            order = paypalrestsdk.Order(
                {
                    "intent": "CAPTURE",
                    "purchase_units": [
                        {
                            "amount": {
                                "currency_code": self.currency,
                                "value": str(self.amount),
                            },
                            "description": f"Payment for borrowing id {self.borrowing.id}",
                        }
                    ],
                    "application_context": {
                        "return_url": f"{base_url}success/",
                        "cancel_url": f"{base_url}cancel/",
                    },
                }
            )

            if order.create():
                self.paypal_order_id = order.id
                self.save()
                for link in order.links:
                    if link.rel == "approve":
                        return link.href
            else:
                raise ValueError(f"PayPal order creation failed: {order.error}")
        except ResourceNotFound as e:
            raise ValueError(f"Resource not found: {str(e)}")
        except ClientError as e:
            raise ValueError(f"Client error: {str(e)}")
        except ServerError as e:
            raise ValueError(f"Server error: {str(e)}")
        except ConnectionError as e:
            raise ValueError(f"Connection error: {str(e)}")
        except MissingConfig as e:
            raise ValueError(f"Missing configuration: {str(e)}")
        except InvalidConfig as e:
            raise ValueError(f"Invalid configuration: {str(e)}")
        except Exception as e:
            raise ValueError(f"An unexpected error occurred: {str(e)}")
