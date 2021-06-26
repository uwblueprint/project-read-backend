from django.test.testcases import TestCase

from enrolments.models import Enrolment, Session, Class
from registration.models import Student, Family
from registration.serializers import EnrolmentPropSerializer
from datetime import date


class EnrolmentPropSerializerTestCase(TestCase):
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
            status=Enrolment.CONFIRMED,
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
                    "facilitator_id": None,
                },
                "enrolled_class": {
                    "id": self.enrolled_class.id,
                    "name": self.enrolled_class.name,
                    "facilitator_id": None,
                },
                "status": self.enrolment.status,
            },
            EnrolmentPropSerializer(self.enrolment).data,
        )
