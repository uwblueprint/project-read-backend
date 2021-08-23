from django.core.exceptions import ValidationError
from django.test import TestCase
from unittest.mock import patch

from accounts.models import User
from enrolments.models import Class, Session
from registration.models import Field
from enrolments.serializers import SessionCreateSerializer
from datetime import date


class SessionCreateSerializerTestCase(TestCase):
    def setUp(self):
        Field.objects.bulk_create(
            [
                Field(
                    role=Field.PARENT,
                    name="Drip or drown?",
                    question="Do you have drip?",
                    question_type=Field.TEXT,
                    is_default=False,
                    order=1,
                ),
                Field(
                    role=Field.CHILD,
                    name="Swag or square?",
                    question="Do you have swag?",
                    question_type=Field.TEXT,
                    is_default=True,
                    order=2,
                ),
                Field(
                    role=Field.GUEST,
                    name="Ice or ill?",
                    question="Do you have ice?",
                    question_type=Field.TEXT,
                    is_default=False,
                    order=3,
                ),
            ]
        )
        self.field_ids = list(Field.objects.values_list("id", flat=True))

        self.name = "Fall 2020"
        self.start_date = date(2020, 9, 5)
        self.fields = [1, 2, 3]
        self.facilitator = User.objects.create(email="user@staff.com")

        self.session_payload = {
            "name": self.name,
            "start_date": self.start_date,
            "fields": self.field_ids,
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

    def test_family_detail_serializer_create(self):
        serializer = SessionCreateSerializer(data=self.session_payload)
        self.assertTrue(serializer.is_valid())
