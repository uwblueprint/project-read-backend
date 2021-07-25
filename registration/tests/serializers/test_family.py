from django.test.testcases import TestCase
from datetime import date

from registration.models import Family, Student
from enrolments.models import Enrolment, Session, Class
from accounts.models import User
from registration.serializers import (
    FamilySerializer,
    StudentSerializer,
)
from enrolments.serializers import EnrolmentSerializer

from datetime import date


class FamilySerializerTestCase(TestCase):
    def setUp(self):
        self.parent1 = Student.objects.create(
            first_name="Merlin",
            last_name="Fischer",
            role=Student.PARENT,
        )
        self.parent2 = Student.objects.create(
            first_name="Gandalf",
            last_name="Whale",
            role=Student.PARENT,
        )
        self.family = Family.objects.create(
            parent=self.parent2,
            email="justkeepswimming@ocean.com",
            cell_number="123456789",
            home_number="1111111111",
            preferred_number="Home",
            address="1 Django Court",
            preferred_comms="Shark Tune",
        )
        self.family_without_children = Family.objects.create(
            parent=self.parent1,
            email="justkeepswimming@ocean.com",
            cell_number="123456789",
            address="42 Wallaby Way",
            preferred_comms="Whale Song",
        )
        self.child1 = Student.objects.create(
            first_name="Albus",
            last_name="Whale",
            role=Student.CHILD,
            family=self.family,
            date_of_birth=date.today(),
        )
        self.child2 = Student.objects.create(
            first_name="Lily",
            last_name="Whale",
            role=Student.CHILD,
            family=self.family,
        )
        self.child3 = Student.objects.create(
            first_name="Harry",
            last_name="Tuna",
            role=Student.CHILD,
            date_of_birth=date(2002, 9, 28),
        )

    def test_family_number(self):
        self.assertEqual(
            {
                "id": self.family.id,
                "parent": StudentSerializer(
                    self.family.parent, context={"request": None}
                ).data,
                "email": self.family.email,
                "phone_number": self.family.home_number,
                "address": self.family.address,
                "preferred_comms": self.family.preferred_comms,
                "num_children": 2,
                "children": [
                    StudentSerializer(self.child1, context={"request": None}).data,
                    StudentSerializer(self.child2, context={"request": None}).data,
                ],
                "current_enrolment": None,
            },
            FamilySerializer(self.family, context={"request": None}).data,
        )

    def test_family_status(self):
        self.parent_with_enrolment = Student.objects.create(
            first_name="Gollum", last_name="Goat", role=Student.PARENT
        )
        self.family_with_multiple_enrolments = Family.objects.create(
            parent=self.parent_with_enrolment,
            email="justkeepswimming@ocean.com",
            cell_number="123456789",
            address="1 Test Ave",
            preferred_comms="Dolphin Whistle",
        )
        self.facilitator = User.objects.create(email="user@staff.com")
        self.session1 = Session.objects.create(
            name="Fall 2019",
            start_date=date(2019, 1, 23),
        )
        self.session2 = Session.objects.create(
            name="Spring 2021",
            start_date=date(2021, 5, 15),
        )
        self.class_from_session1 = Class.objects.create(
            name="Test Class 1",
            session_id=self.session1.id,
            facilitator_id=self.facilitator.id,
            attendance=[],
        )
        self.class_from_session2 = Class.objects.create(
            name="Best Class",
            session_id=self.session2.id,
            facilitator_id=self.facilitator.id,
            attendance=[],
        )
        # These ensure that families with multiple enrolments show the correct enrolment status fields
        self.first_family_enrolment = Enrolment.objects.create(
            active=False,
            family=self.family_with_multiple_enrolments,
            session=self.session1,
            preferred_class=self.class_from_session1,
            enrolled_class=self.class_from_session1,
        )
        self.second_family_enrolment = Enrolment.objects.create(
            active=True,
            family=self.family_with_multiple_enrolments,
            session=self.session2,
            preferred_class=self.class_from_session2,
            enrolled_class=self.class_from_session2,
            status=Enrolment.REGISTERED,
        )
        self.assertEqual(
            {
                "id": self.family_with_multiple_enrolments.id,
                "parent": StudentSerializer(
                    self.family_with_multiple_enrolments.parent,
                    context={"request": None},
                ).data,
                "email": self.family_with_multiple_enrolments.email,
                "phone_number": self.family_with_multiple_enrolments.cell_number,
                "address": self.family_with_multiple_enrolments.address,
                "preferred_comms": self.family_with_multiple_enrolments.preferred_comms,
                "num_children": 0,
                "children": [],
                "current_enrolment": EnrolmentSerializer(
                    self.second_family_enrolment
                ).data,
            },
            FamilySerializer(
                self.family_with_multiple_enrolments, context={"request": None}
            ).data,
        )

    def test_family_serializer_parent(self):
        data = FamilySerializer(self.family_without_children).data
        self.assertEqual(data["parent"], StudentSerializer(self.parent1).data)
        self.assertEqual(data["parent"], StudentSerializer(self.parent1).data)

    def test_family_serializer_children(self):
        data = FamilySerializer(self.family, context={"request": None}).data
        self.assertEqual(data.get("num_children"), 2)

    def test_family_serializer_children_none(self):
        data = FamilySerializer(self.family_without_children).data
        self.assertEqual(data.get("num_children"), 0)
