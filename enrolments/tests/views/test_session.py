from datetime import date
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from enrolments.models import Class, Session
from enrolments.serializers import SessionListSerializer, SessionDetailSerializer


class SessionTestCase(APITestCase):
    def setUp(self):
        self.facilitator = User.objects.create(email="user@staff.com")
        self.class1 = Class.objects.create(
            name="Test Class Create",
            days=[Class.MONDAY, Class.WEDNESDAY],
            location="Waterloo",
            facilitator=self.facilitator.id,
        )
        self.session = Session.objects.create(
            name="Summer 2021", start_date=date(2021, 1, 1)
        )
        self.older_session = Session.objects.create(
            name="Spring 2021", start_date=date(2020, 1, 1)
        )
        self.session_no_start_date = Session.objects.create(
            name="Summer 2021", start_date=None
        )
        self.session_create = Session.objects.create(
            name="Fall 2020",
            start_date=date(2020, 12, 1),
            fields=[1, 2],
            classes=[self.class1],
        )

    def test_get_all_sessions(self):
        url = reverse("session-list")
        self.client.force_authenticate(self.facilitator)
        response = self.client.get(url)
        payload = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # sessions should be ordered by descending start date, with nulls last
        self.assertEqual(
            payload,
            [
                SessionListSerializer(self.session).data,
                SessionListSerializer(self.older_session).data,
                SessionListSerializer(self.session_no_start_date).data,
            ],
        )

    def test_get_session(self):
        url = reverse("session-detail", args=[self.session.id])
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        payload = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(payload, SessionDetailSerializer(self.session).data)

    def test_create_session(self):
        url = reverse("session-detail")
        self.client.force_authenticate(self.user)
        request = {
            "name": self.session_create.name,
            "start_date": self.session_create.days,
            "fields": self.session_create.fields,
            "classes": self.session_create.classes,
        }
        response = self.client.post(url, request, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

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
