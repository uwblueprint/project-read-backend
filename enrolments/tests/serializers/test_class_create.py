from django.core.exceptions import ValidationError
from django.test import TestCase
from unittest.mock import patch
from datetime import date

from accounts.models import User
from enrolments.models import Class, Session
from registration.models import Field
from enrolments.serializers import ClassCreateSerializer


class ClassCreateSerializerTestCase(TestCase):
    def setUp(self):
        self.session = Session.objects.create(
            name="Summer 2021", start_date=date(2021, 1, 1)
        )
        self.name = "Class 1"
        self.days = [Class.MONDAY, Class.THURSDAY]
        self.location = "Waterloo"
        self.facilitator = User.objects.create(email="user@staff.com")

        self.class_payload = {
            "name": self.name,
            "session": self.session.id,
            "days": self.days,
            "location": self.location,
            "facilitator": self.facilitator.id,
        }

    def test_class_serializer_create(self):
        serializer = ClassCreateSerializer(data=dict(self.class_payload))
        self.assertTrue(serializer.is_valid())
        class_obj = serializer.save()

        self.assertEqual(class_obj.attendance, [{"date": "M&G", "attendees": []}])
        self.assertEqual(class_obj.session.id, self.session.id)
