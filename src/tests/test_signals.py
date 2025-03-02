from datetime import datetime, timedelta
from decimal import Decimal

from django.core import mail
from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch

from users.models import User
from books.models import Book
from borrowings.models import Borrowing
from django.db.models.signals import post_save


class RegistrationEmailSignalTest(TestCase):

    @patch(
        "borrowings.signals.render_to_string",
        return_value="<p>Mocked Registration Email Content</p>",
    )
    def test_send_registration_email(self, mock_render):
        mail.outbox = []
        user = User.objects.create_user(
            email="newuser@example.com",
            first_name="John",
            last_name="Doe",
            password="securepassword123",
        )

        post_save.send(sender=get_user_model(), instance=user, created=True)

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]

        self.assertEqual(email.subject, "Welcome to Our Service!")
        self.assertIn("newuser@example.com", email.to)
        self.assertIn("Mocked Registration Email Content", email.body)


class BorrowingEmailSignalTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            username="newuser",
            password="securepassword123",
        )
        book = Book.objects.create(
            title="Test Book Title", pages=200, inventory=10, daily_fee=Decimal("1.50")
        )

        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=book,
            borrow_date=datetime.now().date(),
            expected_return_date=(datetime.now() + timedelta(days=7)).date(),
            status=Borrowing.Status.PENDING,
        )

    @patch(
        "borrowings.signals.render_to_string",
        return_value="<p>Mocked Email Content</p>",
    )
    def test_send_borrowing_confirmation_email(self, mock_render):
        mail.outbox = []

        post_save.send(sender=Borrowing, instance=self.borrowing, created=True)

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]

        self.assertEqual(email.subject, f"Borrowing #{self.borrowing.id} Confirmation")
        self.assertIn("test@example.com", email.to)
        self.assertIn("Mocked Email Content", email.body)

    @patch(
        "borrowings.signals.render_to_string",
        return_value="<p>Mocked Email Content</p>",
    )
    def test_send_borrowing_status_update(self, mock_render):
        mail.outbox = []

        self.borrowing.status = Borrowing.Status.RETURNED
        self.borrowing.save()

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]

        self.assertEqual(email.subject, f"Borrowing {self.borrowing.id} Status Update")
        self.assertIn("test@example.com", email.to)
        self.assertIn("Mocked Email Content", email.body)
