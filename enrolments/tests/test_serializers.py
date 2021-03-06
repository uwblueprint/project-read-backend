# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase
from django.test import TestCase

from accounts.models import User
from registration.models import Family
from registration.models import Student
from registration.serializers import FamilySerializer
from enrolments.serializer import FamilyAttendanceSerializer


class FamilyAttendanceSerializerTestCase(TestCase):
    def setUp(self):
        self.family = Family.objects.create(
            email="fam1@example.com",
            phone_number="123456789",
            address="1 Fam Ave",
            preferred_comms="email",
        )
        self.empty_family = Family.objects.create(
            email="fam2@test.com",
            phone_number="987654321",
            address="2 Fam Ave",
            preferred_comms="email",
        )
        self.student1 = Student.objects.create(
            email="student1@test.com",
            phone_number="987654321",
            address="1 Student Ave",
            preferred_comms="email",
        )
        self.student2 = Student.objects.create(
            email="student2@test.com",
            phone_number="987654321",
            address="2 Student Ave",
            preferred_comms="email",
        )

    def test_serializer1(self):
        self.assertEqual(
            {
                "id": self.family.id,
                "email": self.family.email,
                "phone_number": self.family.phone_number,
                "students:": [
                    {
                        "id": self.student1.id,
                        "first_name": self.student1.first_name,
                        "last_name": self.student1.last_name,
                        "attendee_type": self.student1.attendee_type,
                        "information": self.student1.information,
                    },
                    {
                        "id": self.student2.id,
                        "first_name": self.student2.first_name,
                        "last_name": self.student2.last_name,
                        "attendee_type": self.student2.attendee_type,
                        "information": self.student2.information,
                    },
                ],
            },
            self.family.serialize(),
        )

    def test_serializer2(self):
        self.assertEqual(
            {
                "id": self.empty_family.id,
                "email": self.empty_family.email,
                "phone_number": self.empty_family.phone_number,
                "students:": [],
            },
            self.empty_family.serialize(),
        )
