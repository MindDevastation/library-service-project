from django.db import models

from borrowings.models import Borrowing


class Payment(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Is in the process"
        PAID = "PAID", "Successfully paid"

    class Type(models.TextChoices):
        PAYMENT = "PAYMENT", "Common payment"
        FINE = "FINE", "Penalty"

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    type = models.CharField(max_length=10, choices=Type.choices, default=Type.PAYMENT)
    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, related_name="payments"
    )
    session_url = models.URLField()
    session_id = models.IntegerField()
    models.DecimalField(max_digits=5, decimal_places=2)
