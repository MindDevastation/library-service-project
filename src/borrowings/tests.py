from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.test import APIClient
from rest_framework import status

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
)
from books.models import Book, Author
from borrowings.validators import ActiveBorrowingsLimitValidator
from payments.models import PayPalPayment, StripePayment


class BorrowingSerializerTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@example.com", password="password"
        )
        self.author = Author.objects.create(name="Author Name")
        self.book = Book.objects.create(
            title="Book Title",
            pages=100,
            inventory=1,
            daily_fee=1.00,
            cover=Book.CoverType.HARD,
        )
        self.book_2 = Book.objects.create(
            title="Book Title 2",
            pages=100,
            inventory=1,
            daily_fee=1.00,
            cover=Book.CoverType.HARD,
        )
        self.book.authors.add(self.author)
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=7),
            status=Borrowing.Status.PENDING,
        )

    def test_borrowing_list_serializer(self):
        serializer = BorrowingListSerializer(instance=self.borrowing)
        data = serializer.data
        self.assertEqual(data["user_email"], self.user.email)
        self.assertEqual(data["book_title"], self.book.title)
        self.assertEqual(len(data["book_authors"]), 1)
        self.assertEqual(data["book_authors"][0]["name"], self.author.name)

    def test_borrowing_detail_serializer(self):
        serializer = BorrowingDetailSerializer(instance=self.borrowing)
        data = serializer.data
        self.assertEqual(data["user_email"], self.user.email)
        self.assertEqual(data["book"]["title"], self.book.title)
        self.assertEqual(data["status"], Borrowing.Status.PENDING)

    def test_borrowing_create_serializer_valid(self):
        data = {
            "book": self.book_2.id,
            "expected_return_date": date.today() + timedelta(days=7),
        }
        serializer = BorrowingCreateSerializer(
            data=data, context={"request": type("Request", (), {"user": self.user})()}
        )
        self.assertTrue(serializer.is_valid())
        borrowing = serializer.save()
        self.assertEqual(borrowing.user, self.user)
        self.assertEqual(borrowing.book, self.book_2)
        self.assertEqual(borrowing.status, Borrowing.Status.PENDING)
        self.book_2.refresh_from_db()
        self.assertEqual(self.book_2.inventory, 0)

    def test_borrowing_create_serializer_invalid_book(self):
        unavailable_book = Book.objects.create(
            title="Unavailable Book",
            pages=100,
            inventory=0,
            daily_fee=1.00,
            cover=Book.CoverType.HARD,
        )
        data = {
            "book": unavailable_book.id,
            "expected_return_date": date.today() + timedelta(days=7),
        }
        serializer = BorrowingCreateSerializer(
            data=data, context={"request": type("Request", (), {"user": self.user})()}
        )
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_borrowing_create_serializer_duplicate(self):
        data = {
            "book": self.book.id,
            "expected_return_date": date.today() + timedelta(days=7),
        }
        serializer = BorrowingCreateSerializer(
            data=data, context={"request": type("Request", (), {"user": self.user})()}
        )
        with self.assertRaises(serializers.ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn(
            "You already have an active borrowing for this book", str(context.exception)
        )

    def test_borrowing_create_serializer_invalid_date(self):
        data = {
            "book": self.book.id,
            "expected_return_date": date.today() - timedelta(days=1),
        }
        serializer = BorrowingCreateSerializer(
            data=data, context={"request": type("Request", (), {"user": self.user})()}
        )
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_borrowing_create_serializer_invalid_date_in_future(self):
        data = {
            "book": self.book.id,
            "expected_return_date": date.today() + timedelta(days=31),
        }
        serializer = BorrowingCreateSerializer(
            data=data, context={"request": type("Request", (), {"user": self.user})()}
        )
        with self.assertRaises(serializers.ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn(
            "Expected return date cannot be more than", str(context.exception)
        )

    def test_validator_raises_when_exceeds_limit(self):
        Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=7),
            status=Borrowing.Status.PENDING,
        )
        Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=7),
            status=Borrowing.Status.PENDING,
        )
        validator = ActiveBorrowingsLimitValidator(max_active=2)
        with self.assertRaises(serializers.ValidationError) as context:
            validator(self.user)
        self.assertIn(
            "You already have the maximum number of active borrowings",
            str(context.exception),
        )


class BorrowingViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@example.com", password="password"
        )
        self.other_user = get_user_model().objects.create_user(
            email="other@example.com", password="password"
        )
        self.admin = get_user_model().objects.create_superuser(
            email="admin@example.com", password="adminpassword"
        )
        self.book = Book.objects.create(
            title="Test Book",
            pages=100,
            inventory=1,
            daily_fee=1.00,
            cover=Book.CoverType.HARD,
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=7),
            status=Borrowing.Status.PENDING,
        )
        self.other_borrowing = Borrowing.objects.create(
            user=self.other_user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=7),
            status=Borrowing.Status.PENDING,
        )

    def test_unauthenticated_user_cannot_access(self):
        response = self.client.get("/api/borrowings/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.post(f"/api/borrowings/{self.borrowing.id}/return/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_borrowings_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/borrowings/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["user_email"], self.user.email)

    def test_list_borrowings_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/borrowings/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_filter_is_active_true(self):
        Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=7),
            status=Borrowing.Status.RETURNED,
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/borrowings/?is_active=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_is_active_false(self):
        Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=7),
            status=Borrowing.Status.RETURNED,
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/borrowings/?is_active=false")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["status"], Borrowing.Status.RETURNED
        )

    def test_filter_user_id_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f"/api/borrowings/?user_id={self.user.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_retrieve_borrowing(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/borrowings/{self.borrowing.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user_email"], self.user.email)

    def test_retrieve_borrowing_user_only_own(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/borrowings/{self.other_borrowing.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_borrowing_admin_access(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f"/api/borrowings/{self.other_borrowing.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_borrowing(self):
        self.client.force_authenticate(user=self.user)
        new_book = Book.objects.create(
            title="New Book",
            pages=100,
            inventory=1,
            daily_fee=1.00,
            cover=Book.CoverType.HARD,
        )
        data = {
            "book": new_book.id,
            "expected_return_date": str(date.today() + timedelta(days=7)),
        }
        response = self.client.post("/api/borrowings/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_book.refresh_from_db()
        self.assertEqual(new_book.inventory, 0)

    def test_create_borrowing_invalid_book(self):
        self.client.force_authenticate(user=self.user)
        unavailable_book = Book.objects.create(
            title="Unavailable Book",
            pages=100,
            inventory=0,
            daily_fee=1.00,
            cover=Book.CoverType.HARD,
        )
        data = {
            "book": unavailable_book.id,
            "expected_return_date": str(date.today() + timedelta(days=7)),
        }
        response = self.client.post("/api/borrowings/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_borrowing_with_pending_paypal_payment(self):
        self.client.force_authenticate(user=self.user)
        PayPalPayment.objects.create(
            borrowing=self.borrowing,
            status=PayPalPayment.Status.PENDING,
            amount=Decimal("10.00"),
            borrow_date=self.borrowing.borrow_date,
        )
        new_book = Book.objects.create(
            title="Book With Pending Payment",
            pages=100,
            inventory=1,
            daily_fee=1.00,
            cover=Book.CoverType.HARD,
        )

        data = {
            "book": new_book.id,
            "expected_return_date": str(date.today() + timedelta(days=7)),
        }

        response = self.client.post("/api/borrowings/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("pending payments", response.data.get("detail", "").lower())

    def test_create_borrowing_with_pending_stripe_payment(self):
        self.client.force_authenticate(user=self.user)
        StripePayment.objects.create(
            borrowing=self.borrowing,
            status=PayPalPayment.Status.PENDING,
            amount=Decimal("10.00"),
            borrow_date=self.borrowing.borrow_date,
        )
        new_book = Book.objects.create(
            title="Book With Pending Payment",
            pages=100,
            inventory=1,
            daily_fee=1.00,
            cover=Book.CoverType.HARD,
        )

        data = {
            "book": new_book.id,
            "expected_return_date": str(date.today() + timedelta(days=7)),
        }

        response = self.client.post("/api/borrowings/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("pending payments", response.data.get("detail", "").lower())

    def test_return_book(self):
        self.client.force_authenticate(user=self.user)
        providers = [
            (
                "stripe",
                "https://stripe.com/pay/123",
                "payments.helpers.create_stripe_payment",
            ),
            (
                "paypal",
                "https://paypal.com/approval/456",
                "payments.helpers.create_paypal_payment",
            ),
        ]
        for provider, expected_url, patch_target in providers:
            self.borrowing.status = Borrowing.Status.PENDING
            self.borrowing.save()
            self.book.inventory = 1
            self.book.save()

            with patch(patch_target) as mock_payment:
                if provider == "stripe":
                    mock_session = MagicMock()
                    mock_session.url = expected_url
                    mock_payment.return_value = (None, mock_session)
                else:
                    mock_payment.return_value = (None, expected_url)
                response = self.client.post(
                    f"/api/borrowings/{self.borrowing.id}/return/",
                    {"provider": provider, "currency": "USD"},
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(
                    response.data["message"], "Borrowing returned successfully"
                )
                self.assertEqual(response.data["go_to_pay"], expected_url)

            self.borrowing.refresh_from_db()
            self.book.refresh_from_db()
            self.assertEqual(self.borrowing.status, Borrowing.Status.RETURNED)
            self.assertEqual(self.book.inventory, 2)

    def test_return_already_returned_book(self):
        self.borrowing.status = Borrowing.Status.RETURNED
        self.borrowing.save()
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f"/api/borrowings/{self.borrowing.id}/return/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_book_user_cannot_return_others(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f"/api/borrowings/{self.other_borrowing.id}/return/"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_return_book_admin_can_return_any(self):
        self.client.force_authenticate(user=self.admin)
        providers = [
            (
                "stripe",
                "https://stripe.com/pay/456",
                "payments.helpers.create_stripe_payment",
            ),
            (
                "paypal",
                "https://paypal.com/approval/789",
                "payments.helpers.create_paypal_payment",
            ),
        ]
        for provider, expected_url, patch_target in providers:
            self.other_borrowing.status = Borrowing.Status.PENDING
            self.other_borrowing.save()

            with patch(patch_target) as mock_payment:
                if provider == "stripe":
                    mock_session = MagicMock()
                    mock_session.url = expected_url
                    mock_payment.return_value = (None, mock_session)
                else:
                    mock_payment.return_value = (None, expected_url)
                response = self.client.post(
                    f"/api/borrowings/{self.other_borrowing.id}/return/",
                    {"provider": provider, "currency": "USD"},
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(
                    response.data["message"], "Borrowing returned successfully"
                )
                self.assertEqual(response.data["go_to_pay"], expected_url)

            self.other_borrowing.refresh_from_db()
            self.assertEqual(self.other_borrowing.status, Borrowing.Status.RETURNED)
