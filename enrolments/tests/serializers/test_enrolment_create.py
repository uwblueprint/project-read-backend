from django.core.exceptions import ValidationError
from registration.serializers import FamilyDetailSerializer
from django.test import TestCase
from unittest.mock import patch

from registration.models import Family, Field, Student
from enrolments.models import Class, Session, Enrolment
from enrolments.serializers import EnrolmentCreateSerializer
from datetime import date


class EnrolmentCreateSerializerTestCase(TestCase):
    def setUp(self):
        self.parent_field = Field.objects.create(
            role=Field.PARENT,
            name="Internet Access",
            question="Do you have access to internet",
            question_type=Field.TEXT,
            is_default=True,
            order=1,
        )
        self.child_field = Field.objects.create(
            role=Field.CHILD,
            name="Gender",
            question="What is their gender?",
            question_type=Field.MULTIPLE_CHOICE,
            is_default=True,
            order=1,
        )
        self.guest_field = Field.objects.create(
            role=Field.GUEST,
            name="Relationship",
            question="What's their relationship to your family?",
            question_type=Field.MULTIPLE_CHOICE,
            is_default=True,
            order=1,
        )
        self.session = Session.objects.create(
            season="Spring",
            year=2021,
            start_date=date(2021, 5, 15),
        )
        self.class_in_session = Class.objects.create(
            name="Test Class",
            session_id=self.session.id,
            facilitator_id=None,
            attendance=[],
        )
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
            "role": "Parent",
        }
        self.children_data = [
            {
                "first_name": "Ron",
                "last_name": "Weasley",
                "information": {f"{self.child_field.id}": "male"},
                "role": "Child",
            },
            {
                "first_name": "Ginny",
                "last_name": "Weasley",
                "information": {f"{self.child_field.id}": "female"},
                "role": "Child",
            },
        ]
        self.guests_data = [
            {
                "first_name": "Harry",
                "last_name": "Potter",
                "information": {f"{self.guest_field.id}": "friend"},
                "role": "Guest",
            }
        ]

        self.family_payload = dict(self.family_data)
        self.family_payload["parent"] = self.parent_data
        self.family_payload["children"] = self.children_data
        self.family_payload["guests"] = self.guests_data

        self.enrolment_payload = {
            "family": self.family_payload,
            "session": self.session.id,
            "preferred_class": self.class_in_session.id,
            "status": Enrolment.REGISTERED,
        }

    @patch("registration.serializers.FamilyDetailSerializer.create")
    def test_family_detail_serializer_create(self, mock_create):
        serializer = EnrolmentCreateSerializer(data=self.enrolment_payload)
        family = Family.objects.create(**self.family_data)
        students = [self.parent_data] + self.children_data + self.guests_data
        Student.objects.bulk_create(
            Student(**student, family=family) for student in students
        )
        family.parent = Student.objects.get(family=family, role=Student.PARENT)

        mock_create.return_value = family
        self.assertTrue(serializer.is_valid())
        enrolment = serializer.save()

        self.assertEqual(enrolment.family, family)
        self.assertEqual(enrolment.preferred_class, self.class_in_session)
        self.assertEqual(enrolment.session, self.session)
        self.assertEqual(enrolment.status, Enrolment.REGISTERED)
        mock_create.assert_called_once_with(None, self.family_payload)

    @patch("enrolments.serializers.validate_class_in_session")
    def test_enrolment_create_serializer_validate(self, mock_validate):
        self.assertTrue(
            EnrolmentCreateSerializer(data=self.enrolment_payload).is_valid()
        )
        mock_validate.assert_called_once_with(self.class_in_session, self.session)

    @patch(
        "enrolments.serializers.validate_class_in_session",
        side_effect=ValidationError(""),
    )
    def test_enrolment_create_serializer_validate__invalid(self, mock_validate):
        self.assertFalse(
            EnrolmentCreateSerializer(data=self.enrolment_payload).is_valid()
        )
        mock_validate.assert_called_once_with(self.class_in_session, self.session)
