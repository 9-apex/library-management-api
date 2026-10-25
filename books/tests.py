from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Author, Book, Category


class BooksAPITests(APITestCase):
    def setUp(self):
        self.author = Author.objects.create(
            name="Robert C. Martin",
            biography="Software engineer and author",
            birth_date="1952-12-05",
        )
        self.category = Category.objects.create(
            name="Programming",
            description="Programming books",
        )
        self.book = Book.objects.create(
            title="Clean Code",
            author=self.author,
            category=self.category,
            isbn="9780132350884",
            description="A book about clean code",
            published_date="2008-08-01",
            available_copies=5,
        )
        self.user = User.objects.create_user(
            username="reader",
            password="StrongUserPass2026!",
        )
        self.admin_user = User.objects.create_user(
            username="librarian",
            password="StrongAdminPass2026!",
            is_staff=True,
        )

    def book_data(self):
        return {
            "title": "Python Programming",
            "author": self.author.id,
            "category": self.category.id,
            "isbn": "9780139999999",
            "description": "Python programming guide",
            "published_date": "2024-01-01",
            "available_copies": 10,
        }

    def test_guest_can_view_books(self):
        response = self.client.get("/api/books/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_guest_cannot_create_book(self):
        response = self.client.post(
            "/api/books/",
            self.book_data(),
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_user_cannot_delete_book(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/api/books/{self.book.id}/")
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_admin_can_manage_books(self):
        self.client.force_authenticate(user=self.admin_user)

        created = self.client.post(
            "/api/books/",
            self.book_data(),
            format="json",
        )
        self.assertEqual(
            created.status_code,
            status.HTTP_201_CREATED,
        )

        book_id = created.data["id"]
        updated = self.client.patch(
            f"/api/books/{book_id}/",
            {"available_copies": 20},
            format="json",
        )
        self.assertEqual(
            updated.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(updated.data["available_copies"], 20)

        deleted = self.client.delete(f"/api/books/{book_id}/")
        self.assertEqual(
            deleted.status_code,
            status.HTTP_204_NO_CONTENT,
        )

    def test_duplicate_isbn(self):
        self.client.force_authenticate(user=self.admin_user)
        data = self.book_data()
        data["isbn"] = self.book.isbn

        response = self.client.post(
            "/api/books/",
            data,
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_negative_copies(self):
        self.client.force_authenticate(user=self.admin_user)
        data = self.book_data()
        data["available_copies"] = -5

        response = self.client.post(
            "/api/books/",
            data,
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_nonexistent_book(self):
        response = self.client.get("/api/books/99999/")
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_search_books(self):
        response = self.client.get(
            "/api/books/",
            {"search": "Clean"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_filter_books_by_author(self):
        other_author = Author.objects.create(
            name="Another Author",
            biography="Another biography",
            birth_date="1980-01-01",
        )
        Book.objects.create(
            title="History Book",
            author=other_author,
            category=self.category,
            isbn="9780139999982",
            description="History guide",
            published_date="2020-01-01",
            available_copies=3,
        )

        response = self.client.get(
            "/api/books/",
            {"author": self.author.id},
        )
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["title"],
            "Clean Code",
        )

    def test_pagination(self):
        for i in range(6):
            Book.objects.create(
                title=f"Django Book {i}",
                author=self.author,
                category=self.category,
                isbn=f"9780132350{i:03d}",
                description="Django tutorial",
                published_date="2024-01-01",
                available_copies=2,
            )

        response = self.client.get("/api/books/")
        self.assertEqual(response.data["count"], 7)
        self.assertEqual(len(response.data["results"]), 5)
        self.assertIsNotNone(response.data["next"])

        second_page = self.client.get(
            "/api/books/",
            {"page": 2},
        )
        self.assertEqual(len(second_page.data["results"]), 2)

    def test_protected_author_delete(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(
            f"/api/authors/{self.author.id}/"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )