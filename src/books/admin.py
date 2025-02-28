from django.contrib import admin
from .models import Author, Book


class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "pages", "inventory", "daily_fee")
    search_fields = ("title", "authors__name")
    list_filter = ("authors",)


admin.site.register(Author)
admin.site.register(Book, BookAdmin)
