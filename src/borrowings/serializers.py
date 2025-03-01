from rest_framework import serializers

from books.serializers import AuthorSerializer, BookSerializer
from borrowings.models import Borrowing


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
