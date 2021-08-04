from django.test import TestCase

from enrolments.models import Session
from enrolments.serializers import (
    ClassListSerializer,
    SessionListSerializer,
)
from enrolments.tests.utils.utils import create_test_classes

context = {"request": None}


class SessionListSerializerTestCase(TestCase):
    def setUp(self):
        self.session = Session.objects.create(
            name="Spring 2020",
            fields=[1, 2, 3],
        )
        self.session_class = create_test_classes(self.session, 1)[0]
        self.other_session_class = create_test_classes(self.session, 1)[0]

    def test_session_detail_serializer(self):
        self.assertEqual(
            {
                "id": self.session.id,
                "name": self.session.name,
                "classes": [
                    ClassListSerializer(self.session_class).data,
                    ClassListSerializer(self.other_session_class).data,
                ],
            },
            SessionListSerializer(self.session, context=context).data,
        )
