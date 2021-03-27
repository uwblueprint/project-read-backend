from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from enrolments.models import Class, Session, Enrolment
from registration.models import Family, Student
from enrolments.serializers import ClassDetailSerializer


class ClassesTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="user@staff.com")
        self.session1 = Session.objects.create(season=Session.SPRING, year=2021)
        self.session2 = Session.objects.create(season=Session.FALL, year=2020)
        self.family1 = Family.objects.create(
            email="fam1@test.com",
            phone_number="123456789",
            address="1 Fam St",
            preferred_comms="email",
        )
        self.student1 = Student.objects.create(
            first_name="Student1 FirstName",
            last_name="Student1 LastName",
            role="Child",
            family=self.family1,
            information="null",
        )
        self.class1 = Class.objects.create(
            name="Test Class 1",
            session_id=self.session1.id,
            facilitator_id=self.user.id,
            attendance=[{"date": "2020-01-01", "attendees": [1]}],
        )
        self.empty_class = Class.objects.create(
            name="Test Empty Class",
            session_id=self.session2.id,
            facilitator_id=self.user.id,
            attendance=[{"date": "2020-01-01", "attendees": []}],
        )
        self.enrolment1 = Enrolment.objects.create(
            active=True,
            family=self.family1,
            session=self.session1,
            preferred_class=self.class1,
            enrolled_class=self.class1,
        )

    def test_get_class(self):
        url = reverse("classes-detail", args=[self.class1.id])
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        payload = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            payload,
            ClassDetailSerializer(self.class1).data,
        )

    def test_get_classes(self):
        url = reverse("classes-list")
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        payload = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            payload,
            [
                ClassDetailSerializer(self.class1).data,
                ClassDetailSerializer(self.empty_class).data,
            ],
        )

    def test_method_not_allowed(self):
        url = reverse("classes-detail", args=[self.class1.id])
        self.client.force_authenticate(self.user)

        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_unauthorized(self):
        url = reverse("classes-detail", args=[self.class1.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
