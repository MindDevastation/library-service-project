from rest_framework import generics
from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class AuthorListCreateView(generics.ListCreateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]


class AuthorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]


class BookListCreateView(generics.ListCreateAPIView):
    serializer_class = BookSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Book.objects.prefetch_related("authors")

        title = self.request.query_params.get("title", None)
        if title:
            queryset = queryset.filter(title__icontains=title)

        author_id = self.request.query_params.get("author", None)
        if author_id:
            queryset = queryset.filter(authors=author_id)
        return queryset

    def perform_create(self, serializer):
        authors_data = self.request.data.get("authors", [])
        authors = []

        for author_name in authors_data:
            author, created = Author.objects.get_or_create(name=author_name)
            authors.append(author)

        book = serializer.save()
        book.authors.set(authors)


class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Book.objects.prefetch_related("authors")
        return queryset
