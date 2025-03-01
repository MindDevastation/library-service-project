from django.db import transaction
from rest_framework import serializers

from books.models import Book
from books.serializers import AuthorSerializer, BookSerializer
from borrowings.models import Borrowing
from borrowings.validators import (
    BookAvailabilityValidator,
    BorrowingUniqueValidator,
    ExpectedReturnDateValidator,
)


class BorrowingListSerializer(serializers.ModelSerializer):

    user_email = serializers.CharField(source="user.email")
    book_title = serializers.CharField(source="book.title")
    book_authors = AuthorSerializer(source="book.authors", many=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "user_email",
            "book_title",
            "book_authors",
            "borrow_date",
            "expected_return_date",
            "status",
        ]


class BorrowingDetailSerializer(serializers.ModelSerializer):

    user_email = serializers.CharField(source="user.email")
    book = BookSerializer()

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "user_email",
            "book",
            "borrow_date",
            "expected_return_date",
            "status",
        ]


class BorrowingCreateSerializer(serializers.ModelSerializer):

    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "book",
            "expected_return_date",
        ]

    def validate_book(self, book):
        validator = BookAvailabilityValidator()
        validator(book)
        return book

    def validate_expected_return_date(self, expected_return_date):
        validator = ExpectedReturnDateValidator()
        validator(expected_return_date)
        return expected_return_date

    def validate(self, data):
        user = self.context["request"].user
        book = data.get("book")
        validator = BorrowingUniqueValidator(user=user)
        validator(book)
        return data

    def create(self, validated_data):
        user = self.context["request"].user

        with transaction.atomic():
            book = validated_data.pop("book")
            book.inventory -= 1
            book.save()

            borrowing = Borrowing.objects.create(
                book=book,
                user=user,
                status=Borrowing.Status.PENDING,
                **validated_data,
            )
            return borrowing
