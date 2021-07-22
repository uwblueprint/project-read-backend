from django.test import TestCase

from registration.models import Family, Student
from enrolments.models import Class, Session, Enrolment
from accounts.models import User
from enrolments.serializers import (
    ClassDetailSerializer,
    ClassListSerializer,
    SessionDetailSerializer,
    EnrolmentSerializer,
)
from registration.serializers import FamilySerializer, StudentSerializer
from enrolments.tests.utils.utils import create_test_classes
from datetime import date

context = {"request": None}


class SessionDetailSerializerTestCase(TestCase):
    def setUp(self):
        self.session = Session.objects.create(
            season=Session.SPRING,
            year=2020,
            fields=[1, 2, 3],
        )
        self.session_class = create_test_classes(self.session, 1)[0]
        self.other_session_class = create_test_classes(self.session, 1)[0]
        self.family = Family.objects.create(
            email="weasleys@theorder.com",
            address="12 Grimmauld Pl",
            preferred_comms="Owl Post",
        )
        self.enrolment = Enrolment.objects.create(
            active=True,
            family=self.family,
            session=self.session,
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
                "fields": self.session.fields,
                "classes": [
                    ClassListSerializer(self.session_class).data,
                    ClassListSerializer(self.other_session_class).data,
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
                "attendance": self.class1.attendance,
                "families": [
                    FamilySerializer(self.family1, context={"request": None}).data,
                    FamilySerializer(self.family2, context={"request": None}).data,
                ],
            },
            ClassDetailSerializer(self.class1, context={"request": None}).data,
        )

    def test_empty_class(self):
        self.assertEqual(
            {
                "id": self.empty_class.id,
                "name": self.empty_class.name,
                "attendance": self.empty_class.attendance,
                "families": [],
            },
            ClassDetailSerializer(self.empty_class, context={"request": None}).data,
        )


class EnrolmentSerializerTestCase(TestCase):
    def setUp(self):
        self.parent = Student.objects.create(
            first_name="Gollum", last_name="Goat", role=Student.PARENT
        )
        self.family = Family.objects.create(
            parent=self.parent,
            email="justkeepswimming@ocean.com",
            cell_number="123456789",
            address="1 Test Ave",
            preferred_comms="Dolphin Whistle",
        )
        self.session = Session.objects.create(
            season="Spring",
            year=2021,
            start_date=date(2021, 5, 15),
        )
        self.preferred_class = Class.objects.create(
            name="Preferred Class",
            session_id=self.session.id,
            facilitator_id=None,
            attendance=[],
        )
        self.enrolled_class = Class.objects.create(
            name="Enrolled Class",
            session_id=self.session.id,
            facilitator_id=None,
            attendance=[],
        )
        self.enrolment = Enrolment.objects.create(
            active=False,
            family=self.family,
            session=self.session,
            preferred_class=self.preferred_class,
            enrolled_class=self.enrolled_class,
            status=Enrolment.REGISTERED,
        )

    def test_enrolment_serializer(self):
        self.assertEqual(
            {
                "id": self.enrolment.id,
                "session": {
                    "id": self.session.id,
                    "season": self.session.season,
                    "year": self.session.year,
                },
                "preferred_class": {
                    "id": self.preferred_class.id,
                    "name": self.preferred_class.name,
                },
                "enrolled_class": {
                    "id": self.enrolled_class.id,
                    "name": self.enrolled_class.name,
                },
                "status": self.enrolment.status,
            },
            EnrolmentSerializer(self.enrolment).data,
        )


class EnrolmentCreateSerializerTestCase(TestCase):
    def setUp(self):
        self.family_data = {
            "email": "weasleys@theorder.com",
            "cell_number": "123456789",
            "address": "12 Grimmauld Place",
            "preferred_comms": "Owl Post",
        }
        self.parent_data = {
            "first_name": "Molly",
            "last_name": "Weasley",
            "information": {f"{self.parent_field.id}": "yes"},
        }
        self.children_data = [
            {
                "first_name": "Ron",
                "last_name": "Weasley",
                "information": {f"{self.child_field.id}": "male"},
            },
            {
                "first_name": "Ginny",
                "last_name": "Weasley",
                "information": {f"{self.child_field.id}": "female"},
            },
        ]
        self.guests_data = [
            {
                "first_name": "Harry",
                "last_name": "Potter",
                "information": {f"{self.guest_field.id}": "friend"},
            }
        ]
