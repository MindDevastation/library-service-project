from django.core.validators import MinValueValidator
from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"


class Book(models.Model):
    title = models.CharField(max_length=255)
    pages = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    authors = models.ManyToManyField(Author, related_name="books")
    cover = models.ImageField(null=True, blank=True, upload_to="covers")
    inventory = models.PositiveIntegerField(default=0)
    daily_fee = models.DecimalField(
        max_digits=4, decimal_places=2, validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return self.title

    @property
    def quantity(self):
        borrowed_count = self.borrowings.filter(actual_return_date__isnull=True).count()
        return self.inventory - borrowed_count

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"
        indexes = [
            models.Index(fields=["title"]),
        ]
