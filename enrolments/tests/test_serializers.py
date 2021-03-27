from django.test import TestCase

from registration.models import Family, Student
from enrolments.models import Class, Session, Enrolment
from accounts.models import User
from enrolments.serializers import FamilyAttendanceSerializer, ClassDetailSerializer
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
            role="Child",
            family=self.family1,
            information="null",
        )
        self.student2 = Student.objects.create(
            first_name="Student2 FirstName",
            last_name="Student2 LastName",
            role="Guest",
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
        # self.family2 = Family.objects.create(
        #     email="fam2@test.com",
        #     phone_number="123456789",
        #     address="2 Fam St",
        #     preferred_comms="email",
        # )
        self.session1 = Session.objects.create(
            season="Fall",
            year="2019",
        )
        self.session2 = Session.objects.create(
            season="Spring",
            year="2021",
        )
        self.student1 = Student.objects.create(
            first_name="Student1 FirstName",
            last_name="Student1 LastName",
            role="Child",
            family=self.family1,
            information="null",
        )
        # self.student2 = Student.objects.create(
        #     first_name="Student2 FirstName",
        #     last_name="Student2 LastName",
        #     role="Child",
        #     family=self.family2,
        #     information="null",
        # )
        # self.facilitator = User.objects.create(
        #     username="f1", email="f1@email.com", firebase_uid="test"
        # )
        self.facilitator = User.objects.create(email="user@staff.com")
        self.class1 = Class.objects.create(
            name="Test Class 1",
            session_id=self.session1.id,
            facilitator_id=self.facilitator.id,
            attendance=[{"date": "2020-01-01", "attendees": [1]}],
            # families=[self.family1, self.family2],
        )
        # self.empty_class = Class.objects.create(
        #     name="Test Empty Class",
        #     session_id=self.session2.id,
        #     facilitator_id=self.facilitator.id,
        #     attendance=[{"date": "2020-01-01", "attendees": []}],
        #     # families=[],
        # )
        self.enrolment1 = Enrolment.objects.create(
            active=True,
            family=self.family1,
            session=self.session1,
            preferred_class=self.class1,
            enrolled_class=self.class1,
        )
        # self.enrolment2 = Enrolment.objects.create(
        #     active="True",
        #     family=self.family2,
        #     session=self.session1,
        #     preferred_class=self.class1,
        #     enrolled_class=self.class1,
        # )

    def test_serializer1(self):
        self.maxDiff = None
        self.assertDictEqual(
            {
                "id": self.class1.id,
                "name": self.class1.name,
                "session_id": self.class1.session_id,
                "facilitator_id": self.class1.facilitator_id,
                "attendance": self.class1.attendance,
                "families": [
                    FamilyAttendanceSerializer(
                        self.family1, context={"request": None}
                    ).data,
                    # FamilyAttendanceSerializer(
                    #     self.family2, context={"request": None}
                    # ).data,
                ],
            },
            ClassDetailSerializer(self.class1, context={"request": None}).data,
        )

    # def test_serializer2(self):
    #     self.assertEqual(
    #         {
    #             "id": self.empty_family.id,
    #             "email": self.empty_family.email,
    #             "phone_number": self.empty_family.phone_number,
    #             "students": [],
    #         },
    #         FamilyAttendanceSerializer(
    #             self.empty_family, context={"request": None}
    #         ).data,
    #     )
