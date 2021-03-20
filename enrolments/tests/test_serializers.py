from django.test import TestCase

from registration.models import Family, Student
from enrolments.models import Class, Session
from accounts.models import User
from enrolments.serializers import FamilyAttendanceSerializer
from registration.serializers import StudentSerializer


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

    def test_serializer1(self):
        self.assertEqual(
            {
                "id": self.family1.id,
                "email": self.family1.email,
                "phone_number": self.family1.phone_number,
                "students": [
                    StudentSerializer(self.student1, context={"request": None}).data,
                    StudentSerializer(self.student2, context={"request": None}).data,
                ],
            },
            FamilyAttendanceSerializer(self.family1, context={"request": None}).data,
        )

    def test_serializer2(self):
        self.assertEqual(
            {
                "id": self.empty_family.id,
                "email": self.empty_family.email,
                "phone_number": self.empty_family.phone_number,
                "students": [],
            },
            FamilyAttendanceSerializer(
                self.empty_family, context={"request": None}
            ).data,
        )

class ClassDetailSerializerTestCase(TestCase):
    def setUp(self):
        self.family1 = Family.objects.create(
            email="fam1@test.com",
            phone_number="123456789",
            address="1 Fam St",
            preferred_comms="email",
        )
        self.family2 = Family.objects.create(
            email="fam2@test.com",
            phone_number="123456789",
            address="2 Fam St",
            preferred_comms="email",
        )
        self.session1 = Session.objects.create(
            season="Fall",
            year="2019",
        )
        self.session2 = Session.objects.create(
            season="Spring",
            year="2021",
        )
        self.facilitator = User.objects.create (
            username="f1",
            email="f1@email.com",
            firebase_uid="test"
        )
        self.class1 = Class.objects.create(
            name="Test Class 1",
            session_id = self.session1.id,
            facilitator_id = self.facilitator.id,
            attendance = 'waiting for daniels PR',
            families = [self.family1, self.family2],
        )
        self.empty_class = Class.objects.create(
            name="Test Empty Class",
            session_id = self.session2.id,
            facilitator_id = self.facilitator.id,
            attendance = 'waiting for daniels PR',
            families = [],
        )

    def test_serializer1(self):
        self.assertEqual(
            {
                "id": self.family1.id,
                "email": self.family1.email,
                "phone_number": self.family1.phone_number,
                "students": [
                    StudentSerializer(self.student1, context={"request": None}).data,
                    StudentSerializer(self.student2, context={"request": None}).data,
                ],
            },
            FamilyAttendanceSerializer(self.family1, context={"request": None}).data,
        )

    def test_serializer2(self):
        self.assertEqual(
            {
                "id": self.empty_family.id,
                "email": self.empty_family.email,
                "phone_number": self.empty_family.phone_number,
                "students": [],
            },
            FamilyAttendanceSerializer(
                self.empty_family, context={"request": None}
            ).data,
        )