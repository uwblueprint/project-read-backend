from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from registration.models import Family, Student
from registration.serializers import FamilySerializer, FamilyDetailSerializer


class FamilyTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="user@staff.com")
        self.family = Family.objects.create(
            email="test@example.com",
            cell_number="123456789",
            address="1 Test Ave",
            preferred_comms="email",
        )
        Student.objects.create(
            first_name="Nemo", last_name="Fish", information={"2": "shrimp"}
        )
        self.other_family = Family.objects.create(
            email="example@test.com",
            cell_number="987654321",
            address="2 Test Ave",
            preferred_comms="email",
        )

    def test_get_families(self):
        url = reverse("families-list")
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        payload = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            payload,
            [
                FamilySerializer(self.family).data,
                FamilySerializer(self.other_family).data,
            ],
        )
        self.assertNotEqual(
            payload,
            [
                FamilyDetailSerializer(self.family).data,
                FamilyDetailSerializer(self.other_family).data,
            ],
        )

    def test_get_family(self):
        url = reverse("families-detail", args=[self.family.id])
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        payload = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(payload, FamilySerializer(self.family).data)
        self.assertEqual(payload, FamilyDetailSerializer(self.family).data)

    def test_post_family(self):
        url = reverse("families-list")
        self.client.force_authenticate(self.user)
        response = self.client.post(
            url,
            {
                "email": "weasleys@theorder.com",
                "cell_number": "123456789",
                "address": "12 Grimmauld Place",
                "preferred_comms": "Owl Post",
                "parent": {
                    "first_name": "Molly",
                    "last_name": "Weasley",
                },
                "children": [],
                "guests": [],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_method_not_allowed(self):
        url = reverse("families-detail", args=[self.family.id])
        self.client.force_authenticate(self.user)

        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_unauthorized(self):
        url = reverse("families-list")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        url = reverse("families-detail", args=[self.family.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
