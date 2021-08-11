from accounts.serializers import UserSerializer
from django.urls import NoReverseMatch, reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from unittest.mock import patch


class UserTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="user@staff.com")

    def test_user_detail_url_fail(self):
        with self.assertRaises(NoReverseMatch):
            reverse("user-detail")

    @patch("accounts.serializers.UserCreateSerializer.create")
    def test_post_user(self, mock_method):
        url = reverse("user-list")
        self.client.force_authenticate(self.user)
        response = self.client.post(
            url,
            {
                "email": "test@user.com",
            },
            format="json",
        )
        mock_method.assert_called_with({"email": "test@user.com"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_user__me(self):
        url = reverse("user-list") + "me/"
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), UserSerializer(self.user).data)

    def test_unauthorized(self):
        url = reverse("user-list")
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        url = reverse("user-list") + "me/"
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
