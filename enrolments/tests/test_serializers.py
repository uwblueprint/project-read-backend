from django.test import TestCase

from accounts.models import User
from registration.models import Family
from registration.models import Student
from enrolments.serializers import FamilyAttendanceSerializer
from registration.serializers import StudentSerializer

# todo: not sure if this is needed, i added this to
# fix a prev error but idk if i went down the right path lol
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

factory = APIRequestFactory()
request = factory.get('/')


class FamilyAttendanceSerializerTestCase(TestCase):
    def setUp(self):
        self.family1 = Family.objects.create(
            email="fam1@test.com",
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
            first_name="Student1 FirstName",
            last_name="Student1 LastName",
            attendee_type="Child",
            family=self.family1,
            information="null",
        )
        self.student2 = Student.objects.create(
            first_name="Student2 FirstName",
            last_name="Student2 LastName",
            attendee_type="Guest",
            family=self.family1,
            information="null",
        )
        self.family1less_student2 = Student.objects.create(
            first_name="Student2 FirstName",
            last_name="Student2 LastName",
            attendee_type="Guest",
            family=None,
            information="null",
        )

    def test_serializer1(self):
        self.assertEqual(
            {
                "id": self.family1.id,
                "email": self.family1.email,
                "phone_number": self.family1.phone_number,
                "students": [
                    {
                        "id": self.student1.id,
                        "first_name": self.student1.first_name,
                        "last_name": self.student1.last_name,
                        "attendee_type": self.student1.attendee_type,
                        "family": self.family1.id,
                        "information": self.student1.information,
                    },
                    {
                        "id": self.student2.id,
                        "first_name": self.student2.first_name,
                        "last_name": self.student2.last_name,
                        "attendee_type": self.student2.attendee_type,
                        "family": self.family1.id,
                        "information": self.student2.information,
                    },
                ],
            },
            # FamilyAttendanceSerializer(self.family1).data,
            FamilyAttendanceSerializer(self.family1, context={'request': request}).data,
        )

    def test_serializer2(self):
        self.assertEqual(
            {
                "id": self.empty_family.id,
                "email": self.empty_family.email,
                "phone_number": self.empty_family.phone_number,
                "students": [],
            },
            FamilyAttendanceSerializer(self.empty_family).data,
        )
