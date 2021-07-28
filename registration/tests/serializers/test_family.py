from django.test.testcases import TestCase
from datetime import date

from registration.models import Family, Student
from enrolments.models import Enrolment, Session, Class
from registration.serializers import (
    FamilySerializer,
    StudentSerializer,
)
from enrolments.serializers import EnrolmentSerializer

from datetime import date

context = {"request": None}


class FamilySerializerTestCase(TestCase):
    def setUp(self):
        self.parent = Student.objects.create(
            first_name="Merlin",
            last_name="Fischer",
            role=Student.PARENT,
        )
        self.family = Family.objects.create(
            parent=self.parent,
            email="justkeepswimming@ocean.com",
            cell_number="123456789",
            home_number="1111111111",
            preferred_number="Home",
            address="1 Django Court",
            preferred_comms="Shark Tune",
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

        self.current_session = Session.objects.create(
            season="Spring",
            year=2021,
            start_date=date(2021, 5, 15),
        )
        self.current_class = Class.objects.create(
            name="Current Class",
            session=self.current_session,
            attendance=[],
        )
        self.current_enrolment = Enrolment.objects.create(
            active=True,
            family=self.family,
            session=self.current_session,
            enrolled_class=self.current_class,
        )

        self.past_session = Session.objects.create(
            season="Fall",
            year=2019,
            start_date=date(2019, 1, 23),
        )
        self.past_class = Class.objects.create(
            name="Past Class",
            session=self.past_session,
            attendance=[],
        )
        self.past_enrolment = Enrolment.objects.create(
            active=True,
            family=self.family,
            session=self.past_session,
            enrolled_class=self.past_class,
        )

    def test_family_serializer(self):
        self.assertEqual(
            {
                "id": self.family.id,
                "parent": StudentSerializer(self.family.parent, context=context).data,
                "email": self.family.email,
                "phone_number": self.family.home_number,
                "address": self.family.address,
                "preferred_comms": self.family.preferred_comms,
                "num_children": 2,
                "children": [
                    StudentSerializer(self.child1, context=context).data,
                    StudentSerializer(self.child2, context=context).data,
                ],
                "enrolment": EnrolmentSerializer(
                    self.current_enrolment, context=context
                ).data,
            },
            FamilySerializer(self.family, context=context).data,
        )

    def test_family_serializer_enrolment__specified(self):
        data = FamilySerializer(
            self.family,
            context={
                "request": None,
                "enrolment": EnrolmentSerializer(
                    self.past_enrolment, context=context
                ).data,
            },
        ).data
        self.assertEqual(
            data.get("enrolment"),
            EnrolmentSerializer(self.past_enrolment, context=context).data,
        )
