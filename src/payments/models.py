from decimal import Decimal
from uuid import uuid4

import paypalrestsdk
import stripe
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from paypalrestsdk.exceptions import (
    ResourceNotFound,
    UnauthorizedAccess,
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

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    type = models.CharField(max_length=10, choices=Type.choices, default=Type.PAYMENT)
    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, related_name="%(class)s_payments"
    )
    amount = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
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

    def build_absolute_url(self, request, relative_url):
        return request.build_absolute_uri(relative_url)

    def __str__(self):
        return f"{self.type} payment of {self.amount} on {self.borrow_date}"


class StripePayment(Payment):
    session_id = models.CharField(max_length=255, blank=True, null=True)
    session_url = models.CharField(max_length=512, blank=True, null=True)
    objects = models.Manager()

    def create_checkout_session(self, request):
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY

            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": self.currency.lower(),
                            "product_data": {
                                "name": f"Payment for borrowing id {self.borrowing.id}",
                            },
                            "unit_amount": int(self.amount * 100),
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=self.build_absolute_url(
                    request, reverse("payments:stripe-success")
                )
                + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=self.build_absolute_url(
                    request, reverse("payments:stripe-cancel")
                ),
            )
            self.session_id = session["id"]
            self.session_url = session["url"]
            self.save()
            return session
        except stripe.error.StripeError as error:
            raise ValueError(f"Stripe error occurred: {error.user_message}")


class PayPalPayment(Payment):
    paypal_order_id = models.CharField(max_length=255, blank=True, null=True)
    payer_id = models.CharField(max_length=255, blank=True, null=True)
    approval_url = models.CharField(max_length=512, blank=True, null=True)
    objects = models.Manager()

    def create_order(self, request):
        try:
            paypalrestsdk.configure(
                {
                    "mode": settings.PAYPAL_MODE,
                    "client_id": settings.PAYPAL_CLIENT_ID,
                    "client_secret": settings.PAYPAL_SECRET,
                }
            )

            payment = paypalrestsdk.Payment(
                {
                    "intent": "sale",
                    "payer": {"payment_method": "paypal"},
                    "transactions": [
                        {
                            "amount": {
                                "total": str(self.amount),
                                "currency": self.currency,
                            },
                            "description": f"Payment for borrowing id {self.borrowing.id}",
                        }
                    ],
                    "redirect_urls": {
                        "return_url": self.build_absolute_url(
                            request, reverse("payments:paypal-success")
                        ),
                        "cancel_url": self.build_absolute_url(
                            request, reverse("payments:paypal-cancel")
                        ),
                    },
                }
            )

            if payment.create():
                self.paypal_order_id = payment.id
                for link in payment.links:
                    if link.rel == "approval_url":
                        self.approval_url = link.href
                        break
                self.save()
                return self.approval_url
            else:
                raise ValueError(f"PayPal payment creation failed: {payment.error}")
        except ResourceNotFound as e:
            raise ValueError(f"Resource not found: {str(e)}")
        except UnauthorizedAccess as e:
            raise ValueError(f"Unauthorized access: {str(e)}")
        except Exception as e:
            raise ValueError(f"An unexpected error occurred: {str(e)}")
