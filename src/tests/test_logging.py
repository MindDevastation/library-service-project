import logging
from datetime import datetime
from decimal import Decimal
from io import StringIO
from django.test import TestCase
from unittest.mock import patch
from django.core.exceptions import ValidationError
from django.test import RequestFactory

from logging_app.middleware import ExceptionLoggingMiddleware

from users.models import User
from books.models import Book
from borrowings.models import Borrowing
from payments.models import StripePayment
from logging_app.models import ActionLog


class TestExceptionLoggingMiddleware(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = ExceptionLoggingMiddleware(get_response=lambda request: None)

    @patch("logging_app.middleware.log_error", autospec=True)  # Підміняємо log_error
    def test_standard_django_error_page(self, mock_log_error):
        request = self.factory.get("/some-url/")
        exception = ValidationError(["Invalid data"])

        response = self.middleware.process_exception(request, exception)

        # ✅ Переконуємося, що log_error викликався
        mock_log_error.assert_called_once_with(exception, request)

        # ✅ Переконуємося, що middleware не змінює відповідь (повертає None)
        self.assertIsNone(response)


class LoggingSignalsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@test.com", password="password")
        self.book = Book.objects.create(
            title="Test Book", pages=100, inventory=5, daily_fee=Decimal("1.50")
        )
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            expected_return_date=datetime.strptime("2025-03-10", "%Y-%m-%d").date(),
            status="pending",
        )

        self.logger_output = StringIO()
        self.logger = logging.getLogger("user_actions")
        self.handler = logging.StreamHandler(self.logger_output)
        self.logger.addHandler(self.handler)

    def tearDown(self):
        self.logger.removeHandler(self.handler)
        self.logger_output.close()

    def test_book_create_log(self):
        book = Book.objects.create(
            title="New Book", pages=200, inventory=3, daily_fee=Decimal("1.50")
        )
        log_entry = ActionLog.objects.filter(
            model_name="Book", object_id=book.id, action="created"
        ).first()
        self.assertIsNotNone(log_entry)
        self.assertIn(
            f"Book (ID: {book.id}) New Book was created", self.logger_output.getvalue()
        )

    def test_book_update_log(self):
        self.book.title = "Updated Title"
        self.book.save()
        log_entry = ActionLog.objects.filter(
            model_name="Book", object_id=self.book.id, action="updated"
        ).first()
        self.assertIsNotNone(log_entry)
        self.assertIn(
            f"Book (ID: {self.book.id}) Updated Title was updated",
            self.logger_output.getvalue(),
        )

    def test_book_delete_log(self):
        book_id = self.book.id
        book_title = self.book.title
        self.book.delete()
        log_entry = ActionLog.objects.filter(
            model_name="Book", object_id=book_id, action="deleted"
        ).first()
        self.assertIsNotNone(log_entry)
        self.assertIn(
            f"Book (ID: {book_id}) {book_title} was deleted",
            self.logger_output.getvalue(),
        )

    def test_borrowing_create_log(self):
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            expected_return_date=datetime.strptime("2025-03-10", "%Y-%m-%d").date(),
            status="pending",
        )
        log_entry = ActionLog.objects.filter(
            model_name="Borrowing", object_id=self.borrowing.id, action="created"
        ).first()
        self.assertIsNotNone(log_entry)
        self.assertIn(
            f"User {self.user} created Borrowing (ID: {self.borrowing.id})",
            self.logger_output.getvalue(),
        )

    def test_borrowing_update_log(self):
        self.borrowing.status = "returned"
        self.borrowing.save()
        log_entry = ActionLog.objects.filter(
            model_name="Borrowing", object_id=self.borrowing.id, action="updated"
        ).first()
        self.assertIsNotNone(log_entry)
        self.assertIn(
            f"User {self.user} updated Borrowing (ID: {self.borrowing.id})",
            self.logger_output.getvalue(),
        )

    def test_borrowing_delete_log(self):
        borrowing_id = self.borrowing.id
        self.borrowing.delete()
        log_entry = ActionLog.objects.filter(
            model_name="Borrowing", object_id=borrowing_id, action="deleted"
        ).first()
        self.assertIsNotNone(log_entry)
        self.assertIn(
            f"User {self.user} deleted Borrowing (ID: {borrowing_id})",
            self.logger_output.getvalue(),
        )

    def test_payment_create_log(self):
        payment = StripePayment.objects.create(
            borrowing=self.borrowing, amount=15.00, status="PENDING", currency="USD"
        )
        log_entry = ActionLog.objects.filter(
            model_name="Payment", object_id=payment.id, action="created"
        ).first()
        self.assertIsNotNone(log_entry)
        self.assertIn(f"Payment №{payment.id} created", self.logger_output.getvalue())

    def test_payment_update_log(self):
        payment = StripePayment.objects.create(
            borrowing=self.borrowing, amount=20.00, status="PENDING", currency="USD"
        )
        payment.status = "PAID"
        payment.save()

        log_entry = ActionLog.objects.filter(
            model_name="Payment", object_id=payment.id, action="updated"
        ).first()
        self.assertIsNotNone(log_entry)
        self.assertIn(f"Payment №{payment.id} updated", self.logger_output.getvalue())

    def test_payment_delete_log(self):
        payment = StripePayment.objects.create(
            borrowing=self.borrowing, amount=25.00, status="PENDING", currency="USD"
        )
        payment_id = payment.id
        payment.delete()

        log_entry = ActionLog.objects.filter(
            model_name="Payment", object_id=payment_id, action="deleted"
        ).first()
        self.assertIsNotNone(log_entry)
        self.assertIn(f"Payment №{payment_id} deleted", self.logger_output.getvalue())
