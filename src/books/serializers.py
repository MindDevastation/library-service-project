from rest_framework import serializers
from .models import Author, Book


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "name"]


class BookSerializer(serializers.ModelSerializer):
    quantity = serializers.ReadOnlyField()
    authors = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Author.objects.all()
    )

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "pages",
            "authors",
            "cover",
            "inventory",
            "daily_fee",
            "quantity",
        ]
        read_only_fields = ["id", "quantity"]
        depth = 1
