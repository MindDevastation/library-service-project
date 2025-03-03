import json
import logging
from decimal import Decimal
from io import StringIO
from django.test import TestCase
from unittest.mock import Mock
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import DatabaseError
from requests.exceptions import RequestException
from django.test import RequestFactory

from logging_app.middleware import ExceptionLoggingMiddleware

from users.models import User
from books.models import Book
from borrowings.models import Borrowing
from payments.models import StripePayment
from logging_app.models import ActionLog


class TestExceptionLoggingMiddleware(TestCase):

    @staticmethod
    def _process_exception(request, exception):
        mock_get_response = Mock()
        middleware = ExceptionLoggingMiddleware(get_response=mock_get_response)

        response = middleware.process_exception(request, exception)
        response_data = json.loads(response.content)

        return response, response_data

    def setUp(self):
        self.factory = RequestFactory()
        self.sample_request = self.factory.get("/some-url/")

    def test_validation_error(self):
        request = self.sample_request
        exception = ValidationError("Invalid data")
        response, response_data = self._process_exception(request, exception)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data["error"], "Invalid data")

    def test_request_exception(self):
        request = self.sample_request
        exception = RequestException("API request failed")
        response, response_data = self._process_exception(request, exception)

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response_data["error"], "External API error")
        self.assertEqual(response_data["details"], "API request failed")

    def test_database_error(self):
        request = self.sample_request
        exception = DatabaseError("Database failure")
        response, response_data = self._process_exception(request, exception)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response_data["error"], "Database failure")
        self.assertEqual(response_data["details"], "Database failure")

    def test_permission_denied(self):
        request = self.sample_request
        exception = PermissionDenied("Access denied")
        response, response_data = self._process_exception(request, exception)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_data["error"], "Permission denied")

    def test_key_error(self):
        request = self.sample_request
        exception = KeyError("Missing field")
        response, response_data = self._process_exception(request, exception)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data["error"], "Missing required field")

    def test_attribute_error(self):
        request = self.sample_request
        exception = AttributeError("Invalid attribute")
        response, response_data = self._process_exception(request, exception)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data["error"], "Invalid attribute usage")
        self.assertEqual(response_data["details"], "Invalid attribute")

    def test_type_error(self):
        request = self.sample_request
        exception = TypeError("Invalid type")
        response, response_data = self._process_exception(request, exception)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data["error"], "Invalid data type")
        self.assertEqual(response_data["details"], "Invalid type")

    def test_value_error(self):
        request = self.sample_request
        exception = ValueError("Invalid value")
        response, response_data = self._process_exception(request, exception)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data["error"], "Invalid value")
        self.assertEqual(response_data["details"], "Invalid value")

    def test_generic_error(self):
        request = self.sample_request
        exception = Exception("Something went wrong")
        response, response_data = self._process_exception(request, exception)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response_data["error"], "Something went wrong")


class LoggingSignalsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@test.com", password="password")
        self.book = Book.objects.create(
            title="Test Book", pages=100, inventory=5, daily_fee=Decimal("1.50")
        )
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            expected_return_date="2025-03-10",
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
            expected_return_date="2025-03-10",
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
