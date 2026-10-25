from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=150)
    biography = models.TextField()
    birth_date = models.DateField()

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(
        Author,
        on_delete=models.PROTECT,
        related_name="books",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="books",
    )
    isbn = models.CharField(max_length=13, unique=True)
    description = models.TextField()
    published_date = models.DateField()
    available_copies = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title