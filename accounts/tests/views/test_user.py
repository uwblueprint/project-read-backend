from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from unittest.mock import patch


class UserTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="user@staff.com")

    @patch("accounts.serializers.UserCreateSerializer.create")
    def test_post_user(self, mock_method):
        url = reverse("users-list")
        self.client.force_authenticate(self.user)
        response = self.client.post(
            url,
            {
                "email": "test@user.com",
            },
            format="json",
        )
        self.assertTrue(mock_method.called)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_method_not_allowed(self):
        url = reverse("users-list")
        self.client.force_authenticate(self.user)

        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_unauthorized(self):
        url = reverse("users-list")
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
