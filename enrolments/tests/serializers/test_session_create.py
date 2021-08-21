from django.core.exceptions import ValidationError
from django.test import TestCase
from unittest.mock import patch

from accounts.models import User
from enrolments.models import Class, Session
from enrolments.serializers import SessionCreateSerializer
from datetime import date


class SessionCreateSerializerTestCase(TestCase):
    def setUp(self):
        self.name = "Fall 2020"
        self.start_date = date(2020, 9, 5)
        self.fields = [1, 2, 3]
        self.facilitator = User.objects.create(email="user@staff.com")

        # self.class1 = Class.objects.create(
        #     name="Test Class 1",
        #     days=[Class.TUESDAY, Class.SATURDAY],
        #     location="219 Waterloo Way",
        #     facilitator=self.facilitator.id,
        # )
        # self.class2 = Class.objects.create(
        #     name="Test Class 2",
        #     days=[Class.MONDAY, Class.THURSDAY],
        #     location="1378 Kitchener Street",
        #     facilitator=self.facilitator.id,
        # )
        self.session_payload = {
            "name": self.name,
            "start_date": self.start_date,
            "fields": self.fields,
            # "classes": [self.class1, self.class2],
            "classes": [
                {
                    "name": "Test Class 1",
                    "days": [Class.MONDAY, Class.WEDNESDAY],
                    "location": "129 Waterloo Ave",
                    "facilitator": self.facilitator.id,
                },
                {
                    "name": "Test Class 2",
                    "days": [Class.TUESDAY, Class.THURSDAY],
                    "location": "12 Waterloo Street",
                    "facilitator": self.facilitator.id,
                },
            ],
        }

    # @patch("enrolments.serializers.SessionCreateSerializer.create")
    def test_family_detail_serializer_create(self):
        serializer = SessionCreateSerializer(data=self.session_payload)
        self.assertTrue(serializer.is_valid())
