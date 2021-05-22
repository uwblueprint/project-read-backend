from django.test.testcases import TestCase
from datetime import datetime

from registration.models import Family, Student
from enrolments.models import Enrolment, Session, Class
from accounts.models import User
from registration.serializers import FamilySerializer, StudentSerializer
import pytz


class FamilySerializerTestCase(TestCase):
    def setUp(self):
        self.parent1 = Student.objects.create(
            first_name="Merlin", last_name="Fish", role=Student.PARENT
        )
        self.parent2 = Student.objects.create(
            first_name="Gandalf", last_name="Whale", role=Student.PARENT
        )
        self.parent3 = Student.objects.create(
            first_name="Gollum", last_name="Goat", role=Student.PARENT
        )

        self.family = Family.objects.create(
            parent=self.parent2,
            email="justkeepswimming@ocean.com",
            cell_number="123456789",
            home_number="1111111111",
            preferred_number="Home",
            address="1 Django Boulevard",
            preferred_comms="Shark Tune",
        )

        self.family_without_children = Family.objects.create(
            parent=self.parent1,
            email="justkeepswimming@ocean.com",
            cell_number="123456789",
            address="42 Wallaby Way",
            preferred_comms="Whale Song",
        )

        self.family_status = Family.objects.create(
            parent=self.parent3,
            email="justkeepswimming@ocean.com",
            cell_number="123456789",
            address="1 Test Ave",
            preferred_comms="Dolphin Whistle",
        )

        self.child1 = Student.objects.create(
            first_name="Albus",
            last_name="Whale",
            role=Student.CHILD,
            family=self.family,
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
            family=self.family_status,
        )
        self.session1 = Session.objects.create(
            season="Fall",
            year="2019",
            start_date=datetime(2019, 9, 20, 20, 8, 7, 127325, tzinfo=pytz.UTC)

        )
        self.session2 = Session.objects.create(
            season="Spring",
            year="2021",
            start_date=datetime(2021, 5, 20, 20, 8, 7, 127325, tzinfo=pytz.UTC)
        )
        self.facilitator = User.objects.create(email="user@staff.com")
        self.class1 = Class.objects.create(
            name="Test Class 1",
            session_id=self.session1.id,
            facilitator_id=self.facilitator.id,
            attendance=[{"date": "2019-11-01", "attendees": [1, 2]}],
        )
        self.best_class = Class.objects.create(
            name="Best Class Ever",
            session_id=self.session2.id,
            facilitator_id=self.facilitator.id,
            attendance=[{"date": "2021-05-01", "attendees": [3]}],
        )
        self.enrolment1 = Enrolment.objects.create(
            active=False,
            family=self.family_status,
            session=self.session1,
            preferred_class=self.class1,
            enrolled_class=self.class1,
        )
        self.enrolment2 = Enrolment.objects.create(
            active=True,
            family=self.family_status,
            session=self.session2,
            preferred_class=self.best_class,
            enrolled_class=self.best_class,
            status="Confirmed",
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
                "enrolled": "No",
                "current_class": "N/A",
                "status": "Unassigned",
            },
            FamilySerializer(self.family, context={"request": None}).data,
        )

    def test_family_status(self):
        self.maxDiff = None
        self.assertDictEqual(
            {
                "id": self.family_status.id,
                "parent": StudentSerializer(
                    self.family_status.parent, context={"request": None}
                ).data,
                "email": self.family_status.email,
                "phone_number": self.family_status.cell_number,
                "address": self.family_status.address,
                "preferred_comms": self.family_status.preferred_comms,
                "num_children": 1,
                "enrolled": "Yes",
                "current_class": "Best Class Ever",
                "status": "Confirmed",
            },
            FamilySerializer(self.family_status, context={"request": None}).data,
        )

    def test_family_serializer_parent(self):
        data = FamilySerializer(self.family_without_children).data
        self.assertEqual(data["parent"], StudentSerializer(self.parent1).data)
        self.assertEqual(data["parent"], StudentSerializer(self.parent1).data)

    def test_family_serializer_children(self):
        data = FamilySerializer(self.family).data
        self.assertEqual(data.get("num_children"), 2)

    def test_family_serializer_children_none(self):
        data = FamilySerializer(self.family_without_children).data
        self.assertEqual(data.get("num_children"), 0)
