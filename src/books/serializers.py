from rest_framework import serializers
from .models import Author, Book


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "name"]


class BookSerializer(serializers.ModelSerializer):
    authors = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all(), many=True)
    quantity = serializers.ReadOnlyField()

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

    def create(self, validated_data):
        authors_data = validated_data.pop("authors")
        book = Book.objects.create(**validated_data)
        for author_data in authors_data:
            author, created = Author.objects.get_or_create(**author_data)
            book.authors.add(author)
        return book

    def update(self, instance, validated_data):
        authors_data = validated_data.pop("authors", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if authors_data:
            instance.authors.clear()
            for author_data in authors_data:
                author, created = Author.objects.get_or_create(**author_data)
                instance.authors.add(author)
        instance.save()
        return instance
