from registration.tests.utils.utils import create_test_family, create_test_parent
from django.core.exceptions import ValidationError
from django.test import TestCase
from unittest.mock import call, patch
from datetime import timezone

from enrolments.models import Enrolment
from enrolments.serializers import (
    ClassListSerializer,
    SessionListSerializer,
    EnrolmentSerializer,
)
from enrolments.tests.utils.utils import create_test_classes, create_test_sessions


class EnrolmentSerializerTestCase(TestCase):
    def setUp(self):
        last_name = "Watts"
        self.family = create_test_family(last_name=last_name)
        self.parent = create_test_parent(
            family=self.family,
            last_name=last_name,
        )
        self.session = create_test_sessions(num_sessions=1)[0]
        self.other_session = create_test_sessions(num_sessions=1)[0]
        self.class1 = create_test_classes(
            session=self.session,
            num_classes=1,
        )[0]
        self.class2 = create_test_classes(
            session=self.session,
            num_classes=1,
        )[0]
        self.other_session_class = create_test_classes(
            session=self.other_session,
            num_classes=1,
        )[0]
        self.enrolment = Enrolment.objects.create(
            family=self.family,
            session=self.session,
            preferred_class=self.class1,
            enrolled_class=self.class2,
            status=Enrolment.REGISTERED,
        )
        self.update_request = {
            "id": self.enrolment.id,
            "family": self.family.id,
            "session": self.session.id,
            "preferred_class": self.class2.id,
            "enrolled_class": self.class1.id,
            "status": Enrolment.CLASS_ALLOCATED,
            "students": [self.family.parent.id],
        }

    def test_enrolment_serializer(self):
        self.assertEqual(
            {
                "id": self.enrolment.id,
                "family": self.family.id,
                "session": SessionListSerializer(self.session).data,
                "preferred_class": ClassListSerializer(self.class1).data,
                "enrolled_class": ClassListSerializer(self.class2).data,
                "status": self.enrolment.status,
                "students": [],
                "created_at": self.enrolment.created_at.replace(tzinfo=timezone.utc)
                .astimezone(tz=None)
                .isoformat(),
            },
            EnrolmentSerializer(self.enrolment).data,
        )

    def test_enrolment_serializer__no_classes(self):
        self.enrolment.preferred_class = None
        self.enrolment.enrolled_class = None
        self.assertIsNone(EnrolmentSerializer(self.enrolment).data["preferred_class"])
        self.assertIsNone(EnrolmentSerializer(self.enrolment).data["enrolled_class"])

    @patch("enrolments.serializers.validate_student_ids_in_family")
    @patch("enrolments.serializers.validate_class_in_session")
    def test_enrolment_serializer__validate_create(
        self,
        mock_validate_class_in_session,
        validate_student_ids_in_family,
    ):
        serializer = EnrolmentSerializer(None, data=self.update_request)
        self.assertTrue(serializer.is_valid())
        validate_student_ids_in_family.assert_called_once_with(
            [self.family.parent.id],
            self.family,
        )
        self.assertEqual(mock_validate_class_in_session.call_count, 2)
        mock_validate_class_in_session.assert_has_calls(
            [
                call(self.class2, self.session),
                call(self.class1, self.session),
            ]
        )

    @patch("enrolments.serializers.validate_student_ids_in_family")
    @patch("enrolments.serializers.validate_class_in_session")
    def test_enrolment_serializer__validate_update(
        self,
        mock_validate_class_in_session,
        validate_student_ids_in_family,
    ):
        serializer = EnrolmentSerializer(self.enrolment, data=self.update_request)
        self.assertTrue(serializer.is_valid())
        validate_student_ids_in_family.assert_called_once_with(
            [self.family.parent.id],
            self.family,
        )
        self.assertEqual(mock_validate_class_in_session.call_count, 2)
        mock_validate_class_in_session.assert_has_calls(
            [
                call(self.class2, self.session),
                call(self.class1, self.session),
            ]
        )

    def test_enrolment_serializer_update__cannot_update_family(self):
        other_last_name = "Schmidt"
        other_family = create_test_family(last_name=other_last_name)
        data = dict(self.update_request)
        data["family"] = other_family.id
        serializer = EnrolmentSerializer(self.enrolment, data=data)
        self.assertFalse(serializer.is_valid())

    def test_enrolment_serializer_validate__cannot_update_session(self):
        data = dict(self.update_request)
        data["session"] = self.other_session.id
        serializer = EnrolmentSerializer(self.enrolment, data=data)
        self.assertFalse(serializer.is_valid())

    @patch(
        "enrolments.serializers.validate_student_ids_in_family",
        side_effect=ValidationError(""),
    )
    @patch("enrolments.serializers.validate_class_in_session")
    def test_enrolment_serializer_validate__invalid_update_students(
        self,
        mock_validate_class_in_session,
        validate_student_ids_in_family,
    ):
        serializer = EnrolmentSerializer(self.enrolment, data=self.update_request)
        self.assertFalse(serializer.is_valid())
        validate_student_ids_in_family.assert_called_once_with(
            [self.family.parent.id],
            self.family,
        )
        mock_validate_class_in_session.assert_not_called()

    @patch(
        "enrolments.serializers.validate_student_ids_in_family",
    )
    @patch(
        "enrolments.serializers.validate_class_in_session",
        side_effect=ValidationError(""),
    )
    def test_enrolment_serializer_validate__invalid_update_classes(
        self,
        mock_validate_class_in_session,
        validate_student_ids_in_family,
    ):
        serializer = EnrolmentSerializer(self.enrolment, data=self.update_request)
        self.assertFalse(serializer.is_valid())
        validate_student_ids_in_family.assert_called_once_with(
            [self.family.parent.id],
            self.family,
        )
        mock_validate_class_in_session.assert_called_once_with(
            self.class2,
            self.session,
        )
