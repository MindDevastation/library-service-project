import datetime

from django.db import models
from django.contrib.auth import get_user_model


class Borrowing(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RETURNED = "returned", "Returned"
        OVERDUE = "overdue", "Overdue"

    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=8, choices=Status)
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

    def save(self, *args, **kwargs):
        if self.status == self.Status.RETURNED and not self.actual_return_date:
            self.actual_return_date = datetime.date.today()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"'{self.book.title}' - user: {self.user.email} ({self.status})"
