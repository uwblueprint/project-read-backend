from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from enrolments.models import Session, Class
from enrolments.serializers import (
    SessionSerializer,
    ClassListSerializer,
    SessionDetailsSerializer,
)


class SessionTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="user@staff.com")
        self.session1 = Session.objects.create(season=Session.SPRING, year=2021)
        self.session2 = Session.objects.create(season=Session.FALL, year=2020)
        self.class1 = Class.objects.create(
            name="class1", session=self.session1, facilitator=self.user
        )
        self.class2 = Class.objects.create(
            name="class2", session=self.session1, facilitator=self.user
        )
        self.class3 = Class.objects.create(
            name="class3", session=self.session2, facilitator=self.user
        )

    def test_get_all_sessions(self):
        url = reverse("sessions-list")
        self.client.force_login(self.user)
        response = self.client.get(url)
        payload = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            payload,
            [
                SessionSerializer(self.session1).data,
                SessionSerializer(self.session2).data,
            ],
        )

    def test_get_session(self):
        url = reverse("sessions-detail", args=[self.session1.id])
        self.client.force_login(self.user)
        response = self.client.get(url)
        payload = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(payload, SessionSerializer(self.session1).data)

    def test_get_session1_classes(self):
        url = reverse("sessions-detail", args=[self.session1.id]) + "classes/"
        self.client.force_login(self.user)
        response = self.client.get(url)
        payload = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            payload,
            [
                ClassListSerializer(self.class1).data,
                ClassListSerializer(self.class2).data,
            ],
        )

    def test_get_session2_classes(self):
        url = reverse("sessions-detail", args=[self.session2.id]) + "classes/"
        self.client.force_login(self.user)
        response = self.client.get(url)
        payload = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            payload,
            [
                ClassListSerializer(self.class3).data,
            ],
        )

    def test_method_not_allowed(self):
        url = reverse("sessions-detail", args=[self.session1.id]) + "classes/"
        self.client.force_login(self.user)

        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_unauthorized(self):
        url = reverse("sessions-detail", args=[self.session1.id]) + "classes/"

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
