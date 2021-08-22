from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from registration.models import Field
from registration.serializers import FieldSerializer, FieldListSerializer


class FieldTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="user@staff.com")
        self.parent_field = Field.objects.create(
            role=Field.PARENT,
            name="email",
            question="What is your email?",
            question_type=Field.TEXT,
            is_default=True,
            order=1,
        )
        self.child_field = Field.objects.create(
            role=Field.CHILD,
            name="Date Of Birth",
            question="When were you born?",
            question_type=Field.TEXT,
            is_default=True,
            order=1,
        )
        self.guest_field = Field.objects.create(
            role=Field.GUEST,
            name="Relation to Family",
            question="How are you related?",
            question_type=Field.TEXT,
            is_default=True,
            order=1,
        )

    def test_get_fields(self):
        url = reverse("field-list")
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        payload = response.json()

        serializer = FieldListSerializer(child=FieldSerializer(), data=Field.objects)
        serializer.is_valid()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(payload, serializer.data)

    def test_post_fields(self):
        url = reverse("field-list")
        self.client.force_authenticate(self.user)
        response = self.client.post(
            url,
            {
                "role": Field.CHILD,
                "name": "Favourite Colour",
                "question": "What is your favourite colour",
                "question_type": Field.TEXT,
                "is_default": False,
                "options": [],
                "order": Field.objects.filter(role=Field.CHILD).count() + 1,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_put_fields(self):
        url = reverse("field-detail", args=[self.guest_field.id])
        self.client.force_authenticate(self.user)
        response = self.client.put(
            url,
            {
                "role": self.guest_field.role,
                "name": self.guest_field.name,
                "question": self.guest_field.question,
                "question_type": Field.SELECT,
                "is_default": False,
                "options": ["Aunt, Uncle, Friend, Other"],
                "order": Field.objects.filter(role=Field.GUEST).count() + 1,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_method_not_allowed(self):
        url = reverse("field-detail", args=[self.parent_field.id])
        self.client.force_authenticate(self.user)

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_unauthorized(self):
        url = reverse("field-list")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        url = reverse("field-detail", args=[self.parent_field.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
