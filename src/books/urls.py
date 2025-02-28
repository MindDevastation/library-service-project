from django.urls import path
from books.views import (
    AuthorListCreateView,
    AuthorDetailView,
    BookListCreateView,
    BookDetailView,
)

urlpatterns = [
    path("authors/", AuthorListCreateView.as_view(), name="author-list-create"),
    path("authors/<int:pk>/", AuthorDetailView.as_view(), name="author-detail"),
    path("bookslist/", BookListCreateView.as_view(), name="book-list-create"),
    path("booklist/<int:pk>/", BookDetailView.as_view(), name="book-detail"),
]

app_name = "books"
