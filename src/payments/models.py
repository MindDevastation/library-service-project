from uuid import uuid4

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
    session_url = models.URLField()
    session_id = models.UUIDField(default=uuid4, editable=False, unique=True)
    money_to_pay = models.DecimalField(max_digits=5, decimal_places=2, positive=True)
    borrow_date = models.DateField()
    currency = models.CharField(
        max_length=3, choices=Currency.choices, default=Currency.UAH, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
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
        return f"{self.type} payment of {self.money_to_pay} on {self.borrow_date}"
