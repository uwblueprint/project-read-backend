from django.core.exceptions import ValidationError
from django.test import TestCase
from unittest.mock import patch

from accounts.models import User
from enrolments.models import Class
from enrolments.serializers import ClassCreateSerializer


class ClassCreateSerializerTestCase(TestCase):
    def setUp(self):
        self.name = "Class 1"
        self.days = [Class.MONDAY, Class.THURSDAY]
        self.location = "Waterloo"
        self.facilitator = User.objects.create(email="user@staff.com")

        self.class_payload = {
            "name": self.name,
            "days": self.days,
            "location": self.location,
            "facilitator": self.facilitator.id,
        }

    @patch("enrolments.serializers.ClassCreateSerializer.create")
    def test_class_serializer_create(self, mock_create):
        serializer = ClassCreateSerializer(data=self.class_payload)
        self.assertTrue(serializer.is_valid())
