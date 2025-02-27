from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=255)
    pages = models.IntegerField()
    authors = models.CharField(max_length=255)
    cover = models.ImageField(null=True, blank=True, upload_to="covers")
    inventory = models.IntegerField()
    daily_fee = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return self.title

    @property
    def quantity(self):
        borrowed_count = self.borrowings.filter(actual_return_date__isnull=True).count()
        return self.inventory - borrowed_count

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"

