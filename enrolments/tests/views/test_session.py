from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from enrolments.models import Session
from enrolments.serializers import SessionSerializer


class SessionTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="user@staff.com")
        self.session_1 = Session.objects.create(season=Session.SPRING, year=2021)
        self.session_2 = Session.objects.create(season=Session.SUMMER, year=2021)

    def test_get_all_sessions(self):
        url = reverse("sessions-list")
        self.client.force_login(self.user)
        response = self.client.get(url)
        payload = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            payload,
            [
                SessionSerializer(self.session_1).data,
                SessionSerializer(self.session_2).data,
            ],
        )

    def test_get_session(self):
        url = reverse("sessions-detail", args=[self.session_1.id])
        self.client.force_login(self.user)
        response = self.client.get(url)
        payload = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(payload, SessionSerializer(self.session_1).data)

    def test_post_session(self):
         url = reverse("sessions-list")
         self.client.force_login(self.user)
         response = self.client.post(url)
         self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_method_not_allowed(self):
        url = reverse("sessions-detail", args=[self.session_1.id])
        self.client.force_login(self.user)

        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_unauthorized(self):
        url = reverse("sessions-list")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        url = reverse("sessions-detail", args=[self.session_1.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)