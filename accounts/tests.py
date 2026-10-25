from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken


class AccountsAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="student1",
            email="student1@example.com",
            password="StrongPass2026!",
        )

    def test_registration(self):
        data = {
            "username": "newstudent",
            "email": "newstudent@example.com",
            "password": "VeryStrongPass2026!",
        }
        response = self.client.post(
            "/api/register/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        user = User.objects.get(username="newstudent")
        self.assertTrue(
            user.check_password("VeryStrongPass2026!")
        )
        self.assertNotIn("password", response.data)

    def test_login(self):
        response = self.client.post(
            "/api/login/",
            {
                "username": "student1",
                "password": "StrongPass2026!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_profile_access(self):
        guest = self.client.get("/api/profile/")
        self.assertEqual(
            guest.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        login = self.client.post(
            "/api/login/",
            {
                "username": "student1",
                "password": "StrongPass2026!",
            },
            format="json",
        )
        token = login.data["access"]

        response = self.client.get(
            "/api/profile/",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "student1")

    def test_refresh_token(self):
        login = self.client.post(
            "/api/login/",
            {
                "username": "student1",
                "password": "StrongPass2026!",
            },
            format="json",
        )

        response = self.client.post(
            "/api/token/refresh/",
            {"refresh": login.data["refresh"]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_invalid_token(self):
        response = self.client.get(
            "/api/profile/",
            HTTP_AUTHORIZATION="Bearer invalid.token",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_expired_token(self):
        token = AccessToken.for_user(self.user)
        token["exp"] = int(
            (timezone.now() - timedelta(minutes=1)).timestamp()
        )

        response = self.client.get(
            "/api/profile/",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )