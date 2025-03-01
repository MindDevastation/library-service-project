import datetime

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


class Borrowing(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RETURNED = "returned", "Returned"
        OVERDUE = "overdue", "Overdue"

    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=8, choices=Status.choices)
    book = models.ForeignKey(
        "books.Book", on_delete=models.CASCADE, related_name="borrowings"
    )
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="borrowings"
    )

    class Meta:
        indexes = [
            models.Index(fields=["borrow_date", "expected_return_date", "status"])
        ]

    def clean(self):
        borrow_date = self.borrow_date or datetime.date.today()
        if self.expected_return_date < borrow_date:
            raise ValidationError("Expected return date cannot be before borrow date")

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.status == self.Status.RETURNED and not self.actual_return_date:
            self.actual_return_date = datetime.date.today()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"'{self.book.title}' - user: {self.user.email} ({self.status})"
