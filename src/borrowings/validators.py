from datetime import date, timedelta

from rest_framework.serializers import ValidationError as SerializerValidationError


class BookAvailabilityValidator:

    message = "Book is out of stock"

    def __init__(self, error_class=SerializerValidationError):
        self.error_class = error_class

    def __call__(self, book):
        if book.inventory <= 0:
            raise self.error_class(self.message)
        return book


class ExpectedReturnDateValidator:

    max_days = 30
    message_if_before_borrow = "Expected return date cannot be before borrow date"

    def __init__(self, error_class=SerializerValidationError):
        self.error_class = error_class

    def __call__(self, expected_return_date):
        today = date.today()
        if expected_return_date < today:
            raise self.error_class(self.message_if_before_borrow)
        if expected_return_date > today + timedelta(days=self.max_days):
            raise self.error_class(
                f"Expected return date cannot be more than {self.max_days} days in the future"
            )
        return expected_return_date


class BorrowingUniqueValidator:

    message = "You already has an active borrowing for this book"

    def __init__(self, user, error_class=SerializerValidationError):
        self.user = user
        self.error_class = error_class

    def __call__(self, book):
        from borrowings.models import Borrowing

        if Borrowing.objects.filter(
            book=book,
            user=self.user,
            status__in=[Borrowing.Status.PENDING, Borrowing.Status.OVERDUE],
        ).exists():
            raise self.error_class(self.message)
        return book
