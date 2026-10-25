from rest_framework import serializers
from .models import Author, Book, Category


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "name", "biography", "birth_date"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class BookSerializer(serializers.ModelSerializer):
    author_details = AuthorSerializer(source="author", read_only=True)
    category_details = CategorySerializer(source="category", read_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "author_details",
            "category",
            "category_details",
            "isbn",
            "description",
            "published_date",
            "available_copies",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_isbn(self, value):
        books = Book.objects.filter(isbn=value)

        if self.instance:
            books = books.exclude(pk=self.instance.pk)

        if books.exists():
            raise serializers.ValidationError(
                "A book with this ISBN already exists."
            )

        return value

    def validate_available_copies(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Available copies cannot be negative."
            )

        return value