from datetime import date, timedelta

from rest_framework.serializers import ValidationError as SerializerValidationError


class BookAvailabilityValidator:
    """
    Validator that checks if a book is available for borrowing.
    Raises a ValidationError if the book's inventory is zero or less.
    """

    message = "Book is out of stock"

    def __init__(self, error_class=SerializerValidationError):
        self.error_class = error_class

    def __call__(self, book):
        if book.inventory <= 0:
            raise self.error_class(self.message)
        return book


class ExpectedReturnDateValidator:
    """
    Validator that ensures the expected return date is within an acceptable range.
    The expected return date must not be in the past and must not exceed a specified
    maximum number of days into the future.
    """

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
    """
    Validator that ensures a user does not have an active borrowing for the same book.
    Checks that the user does not already have a borrowing in either 'PENDING' or 'OVERDUE' status
    for the given book.
    """

    message = "You already have an active borrowing for this book"

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


class ActiveBorrowingsLimitValidator:
    """
    Validator that checks if the user has exceeded the maximum number of active borrowings.
    Active borrowings are those with status 'pending' or 'overdue'.
    """

    def __init__(self, max_active=5, error_class=SerializerValidationError):
        self.max_active = max_active
        self.error_class = error_class

    def __call__(self, user):
        from borrowings.models import Borrowing

        active_count = Borrowing.objects.filter(
            user=user, status__in=[Borrowing.Status.PENDING, Borrowing.Status.OVERDUE]
        ).count()
        if active_count >= self.max_active:
            raise self.error_class(
                "You already have the maximum number of active borrowings."
            )
        return user
