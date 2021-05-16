from django.test import TestCase

from registration.models import Family, Student
from enrolments.models import Class, Session, Enrolment
from accounts.models import User
from enrolments.serializers import (
    FamilyAttendanceSerializer,
    ClassDetailSerializer,
    SessionDetailSerializer,
)
from registration.serializers import FamilySerializer, StudentSerializer

context = {"request": None}


class FamilyAttendanceSerializerTestCase(TestCase):
    def setUp(self):
        self.family1 = Family.objects.create(
            email="fam1@test.com",
            cell_number="123456789",
            work_number="0000000000",
            preferred_number="Work",
            address="1 Fam Ave",
            preferred_comms="email",
        )
        self.empty_family = Family.objects.create(
            email="fam2@test.com",
            cell_number="987654321",
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

    def test_family_attendance_serializer(self):
        self.assertEqual(
            {
                "id": self.family1.id,
                "email": self.family1.email,
                "phone_number": self.family1.work_number,
                "students": [
                    StudentSerializer(self.student1, context=context).data,
                    StudentSerializer(self.student2, context=context).data,
                ],
            },
            FamilyAttendanceSerializer(self.family1, context=context).data,
        )

    def test_family_attendance_serializer__no_students(self):
        self.assertEqual(
            {
                "id": self.empty_family.id,
                "email": self.empty_family.email,
                "phone_number": self.empty_family.cell_number,
                "students": [],
            },
            FamilyAttendanceSerializer(self.empty_family, context=context).data,
        )


class SessionDetailSerializerTestCase(TestCase):
    def setUp(self):
        self.session = Session.objects.create(
            season=Session.SPRING,
            year=2020,
        )
        self.facilitator = User.objects.create(email="user@staff.com")
        self.class1 = Class.objects.create(
            name="Cool Class",
            session_id=self.session.id,
            facilitator_id=self.facilitator.id,
            attendance=[{"date": "2020-01-01", "attendees": [1, 2]}],
        )
        self.family = Family.objects.create(
            email="weasleys@theorder.com",
            address="12 Grimmauld Pl",
            preferred_comms="Owl Post",
        )
        self.enrolment = Enrolment.objects.create(
            active=True,
            family=self.family,
            session=self.session,
            enrolled_class=self.class1,
        )
        self.other_family = Family.objects.create(
            email="spongebob@squarepants.com",
            address="1 Pine Apple",
            preferred_comms="Snail Delivery",
        )
        self.other_enrolment = Enrolment.objects.create(
            active=True,
            family=self.other_family,
            session=self.session,
            enrolled_class=self.class1,
        )

    def test_session_detail_serializer(self):
        self.assertEqual(
            {
                "id": self.session.id,
                "season": self.session.season,
                "year": self.session.year,
                "families": [
                    FamilySerializer(self.family, context=context).data,
                    FamilySerializer(self.other_family, context=context).data,
                ],
            },
            SessionDetailSerializer(self.session, context=context).data,
        )


class ClassDetailSerializerTestCase(TestCase):
    def setUp(self):
        self.family1 = Family.objects.create(
            email="fam1@test.com",
            cell_number="123456789",
            address="1 Fam St",
            preferred_comms="email",
        )
        self.family2 = Family.objects.create(
            email="fam2@test.com",
            cell_number="123456789",
            address="2 Fam St",
            preferred_comms="email",
        )
        self.inactive_family = Family.objects.create(
            email="fam3@test.com",
            cell_number="123406789",
            address="3 Fam St",
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
            role="Child",
            family=self.family2,
            information="null",
        )
        self.facilitator = User.objects.create(email="user@staff.com")
        self.class1 = Class.objects.create(
            name="Test Class 1",
            session_id=self.session1.id,
            facilitator_id=self.facilitator.id,
            attendance=[{"date": "2020-01-01", "attendees": [1, 2]}],
        )
        self.empty_class = Class.objects.create(
            name="Test Empty Class",
            session_id=self.session2.id,
            facilitator_id=self.facilitator.id,
            attendance=[{"date": "2020-01-01", "attendees": []}],
        )
        self.enrolment1 = Enrolment.objects.create(
            active=True,
            family=self.family1,
            session=self.session1,
            preferred_class=self.class1,
            enrolled_class=self.class1,
        )
        self.enrolment2 = Enrolment.objects.create(
            active=True,
            family=self.family2,
            session=self.session1,
            preferred_class=self.class1,
            enrolled_class=self.class1,
        )
        self.inactive_enrolment = Enrolment.objects.create(
            active=False,
            family=self.inactive_family,
            session=self.session1,
            preferred_class=self.class1,
            enrolled_class=self.class1,
        )

    def test_serializer1(self):
        self.assertEqual(
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
                    FamilyAttendanceSerializer(
                        self.family2, context={"request": None}
                    ).data,
                ],
            },
            ClassDetailSerializer(self.class1, context={"request": None}).data,
        )

    def test_empty_class(self):
        self.assertEqual(
            {
                "id": self.empty_class.id,
                "name": self.empty_class.name,
                "session_id": self.empty_class.session_id,
                "facilitator_id": self.empty_class.facilitator_id,
                "attendance": self.empty_class.attendance,
                "families": [],
            },
            ClassDetailSerializer(self.empty_class, context={"request": None}).data,
        )
