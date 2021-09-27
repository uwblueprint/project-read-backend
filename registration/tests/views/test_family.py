from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from registration.models import Family, Student
from registration.serializers import (
    FamilySearchSerializer,
    FamilySerializer,
    FamilyDetailSerializer,
)


class FamilyTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="user@staff.com")
        self.family = Family.objects.create(
            email="test@example.com",
            cell_number="123456789",
            address="1 Test Ave",
            preferred_comms="email",
        )
        self.parent = Student.objects.create(
            first_name="Marlin",
            last_name="Fish",
            family=self.family,
        )
        self.other_family = Family.objects.create(
            email="example@test.com",
            cell_number="987654321",
            address="2 Test Ave",
            preferred_comms="email",
        )

    def test_get_families(self):
        url = reverse("family-list")
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
        url = reverse("family-detail", args=[self.family.id])
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        payload = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(payload, FamilySerializer(self.family).data)
        self.assertEqual(payload, FamilyDetailSerializer(self.family).data)

    def test_post_family(self):
        url = reverse("family-list")
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

    def test_put_family(self):
        url = reverse("family-detail", args=[self.family.id])
        self.client.force_authenticate(self.user)
        request = {
            "id": self.family.id,
            "email": self.family.email,
            "cell_number": self.family.cell_number,
            "parent": {
                "id": self.parent.id,
                "first_name": self.parent.first_name,
                "last_name": self.parent.last_name,
                "date_of_birth": "1970-01-01",
                "information": {},
            },
            "children": [],
            "guests": [],
            "enrolments": [],
        }
        self.family.parent = self.parent
        self.family.save()
        response = self.client.put(url, request, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_method_not_allowed(self):
        url = reverse("family-detail", args=[self.family.id])
        self.client.force_authenticate(self.user)

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_unauthorized(self):
        url = reverse("family-list")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        url = reverse("family-detail", args=[self.family.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FamilySearchTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="user@staff.com")
        self.family = Family.objects.create(
            email="test@example.com",
            cell_number="123456789",
            address="1 Test Ave",
            preferred_comms="email",
        )
        self.parent = Student.objects.create(
            first_name="Marlin",
            last_name="Fish",
            family=self.family,
        )
        self.family.parent = self.parent
        self.family.save()

        self.other_family = Family.objects.create(
            email="example@test.com",
            cell_number="987654321",
            address="2 Test Ave",
            preferred_comms="email",
        )
        self.other_parent = Student.objects.create(
            first_name="Marlin",
            last_name="Cow",
            family=self.other_family,
        )
        self.other_family.parent = self.other_parent
        self.other_family.save()

        # student with the same name as self.parent, but in other_family
        Student.objects.create(
            first_name="Marlin",
            last_name="Fish",
            family=self.other_family,
        )

    def test_search_familes_no_params(self):
        url = reverse("family-list") + "search/"
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_familes__parent_only__first_and_last_name(self):
        query_params = {"first_name": "Marlin", "last_name": "Fish"}
        url = (
            reverse("family-list")
            + "search/?parent_only=True&first_name="
            + query_params["first_name"]
            + "&last_name="
            + query_params["last_name"]
        )
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        payload = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            payload,
            [
                FamilySearchSerializer(self.family).data,
            ],
        )

    def test_search_familes_first_and_last_name(self):
        query_params = {"first_name": "Marlin", "last_name": "Fish"}
        url = (
            reverse("family-list")
            + "search/?first_name="
            + query_params["first_name"]
            + "&last_name="
            + query_params["last_name"]
        )
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        payload = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            payload,
            [
                FamilySearchSerializer(self.family).data,
                FamilySearchSerializer(self.other_family).data,
            ],
        )

    def test_search_familes_first_name(self):
        query_params = {
            "first_name": "Marlin",
        }
        url = (
            reverse("family-list") + "search/?first_name=" + query_params["first_name"]
        )
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        payload = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            payload,
            [
                FamilySearchSerializer(self.family).data,
                FamilySearchSerializer(self.other_family).data,
            ],
        )

    def test_method_not_allowed(self):
        url = reverse("family-list") + "search/"
        self.client.force_authenticate(self.user)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_unauthorized(self):
        url = reverse("family-list") + "search/"

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
