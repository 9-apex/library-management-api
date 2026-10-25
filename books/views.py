from django.db.models.deletion import ProtectedError
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from .models import Author, Book, Category
from .permissions import IsAdminOrReadOnly
from .serializers import (
    AuthorSerializer,
    BookSerializer,
    CategorySerializer,
)


class ProtectedDeleteMixin:
    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            raise ValidationError({
                "detail": (
                    "Cannot delete this record because "
                    "it is used by books."
                )
            })


class BookViewSet(viewsets.ModelViewSet):
    queryset = (
        Book.objects.select_related("author", "category")
        .all()
        .order_by("id")
    )
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["title"]
    filterset_fields = ["author", "category"]


class AuthorViewSet(
    ProtectedDeleteMixin,
    viewsets.ModelViewSet,
):
    queryset = Author.objects.all().order_by("id")
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminOrReadOnly]


class CategoryViewSet(
    ProtectedDeleteMixin,
    viewsets.ModelViewSet,
):
    queryset = Category.objects.all().order_by("id")
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]