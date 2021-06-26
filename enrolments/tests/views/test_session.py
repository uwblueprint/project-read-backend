from datetime import date
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from enrolments.models import Session
from enrolments.serializers import SessionSerializer, SessionDetailSerializer


class SessionTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="user@staff.com")
        self.session = Session.objects.create(
            season=Session.SUMMER, year=2021, start_date=date(2021, 1, 1)
        )
        self.older_session = Session.objects.create(
            season=Session.SPRING, year=2021, start_date=date(2020, 1, 1)
        )
        self.session_no_start_date = Session.objects.create(
            season=Session.SUMMER, year=2021, start_date=None
        )

    def test_get_all_sessions(self):
        url = reverse("session-list")
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        payload = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # sessions should be ordered by descending start date, with nulls last
        self.assertEqual(
            payload,
            [
                SessionSerializer(self.session).data,
                SessionSerializer(self.older_session).data,
                SessionSerializer(self.session_no_start_date).data,
            ],
        )

    def test_get_session(self):
        url = reverse("session-detail", args=[self.session.id])
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        payload = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(payload, SessionDetailSerializer(self.session).data)

    def test_method_not_allowed(self):
        url = reverse("session-detail", args=[self.session.id])
        self.client.force_authenticate(self.user)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_unauthorized(self):
        url = reverse("session-list")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        url = reverse("session-detail", args=[self.session.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
