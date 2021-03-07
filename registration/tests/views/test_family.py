from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from registration.models import Family, Student, FamilyInfo
from registration.serializers import FamilyDetailSerializer


class FamilyTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="user@staff.com")
        self.parent_field = FamilyInfo.objects.create(
            name="Internet access", question="Do you have access to internet?"
        )
        self.other_parent_field = FamilyInfo.objects.create(
            name="Allergies", question="Do you have any allergies?"
        )
        self.parent = Student.objects.create(
            first_name="Merlin",
            last_name="Fish",
            attendee_type=Student.PARENT,
            information=[
                {"id": self.parent_field.id, "response": "Yes"},
                {"id": self.other_parent_field.id, "response": "Sharks"},
            ],
        )
        self.family = Family.objects.create(
            parent=self.parent,
            email="test@example.com",
            phone_number="123456789",
            address="1 Test Ave",
            preferred_comms="email",
        )
        self.other_family = Family.objects.create(
            email="example@test.com",
            phone_number="987654321",
            address="2 Test Ave",
            preferred_comms="email",
        )

    def test_get_families(self):
        url = reverse("families-list")
        self.client.force_login(self.user)
        response = self.client.get(url)
        payload = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            payload,
            [
                FamilyDetailSerializer(self.family).data,
                FamilyDetailSerializer(self.other_family).data,
            ],
        )

    def test_get_family(self):
        url = reverse("families-detail", args=[self.family.id])
        self.client.force_login(self.user)
        response = self.client.get(url)
        payload = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(payload, FamilyDetailSerializer(self.family).data)

    def test_post_family(self):
        url = reverse("families-list")
        self.client.force_login(self.user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_method_not_allowed(self):
        url = reverse("families-detail", args=[self.family.id])
        self.client.force_login(self.user)

        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_unauthorized(self):
        url = reverse("families-list")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        url = reverse("families-detail", args=[self.family.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
