from django.core.exceptions import ValidationError
from django.test import TestCase
from unittest.mock import call, patch

from ..models import Student, Field
from ..validators import (
    validate_family_parent,
    validate_information,
    validate_student_role_information,
)


class ValidatorsTestCase(TestCase):
    def setUp(self):
        self.parent = Student.objects.create(
            first_name="Merlin", last_name="Fish", role="Parent"
        )
        self.child = Student.objects.create(
            first_name="Nemo", last_name="Fish", role="Child"
        )
        self.parent_field = Field.objects.create(
            role=Field.PARENT,
            name="DOB",
            question="What's your date of birth?",
            question_type=Field.TEXT,
            is_default=True,
            order=1,
        )
        self.child_field = Field.objects.create(
            role=Field.CHILD,
            name="Allergies",
            question="Do they have any allergies?",
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

    def test_validate_family_parent(self):
        self.assertIsNone(validate_family_parent(self.parent.id))
        self.assertRaises(ValidationError, validate_family_parent, self.child.id)

    def test_validate_information_responses(self):
        pass

    @patch("registration.validators.validate_information_responses")
    def test_validate_information(self, mock_validate_responses):
        information = {f"{self.parent_field.id}": "Yes"}
        is_valid = validate_information(information)
        self.assertIsNone(is_valid)
        mock_validate_responses.assert_called_once()
        self.assertListEqual(
            list(mock_validate_responses.call_args.args[0]),
            list(information.values()),
        )

    @patch("registration.validators.validate_information_responses")
    def test_validate_information__invalid(self, mock_validate_responses):
        information = {f"0": "Yes"}
        self.assertRaises(ValidationError, validate_information, information)
        mock_validate_responses.assert_not_called()

    @patch("registration.validators.validate_information_responses")
    def test_validate_student_role_information(self, mock_validate_responses):
        student = {
            "role": Student.PARENT,
            "information": {
                f"{self.parent_field.id}": "value",
            },
        }
        is_valid = validate_student_role_information(student)
        self.assertIsNone(is_valid)
        mock_validate_responses.assert_called_once()
        self.assertListEqual(
            list(mock_validate_responses.call_args.args[0]),
            list(["value"]),
        )

    @patch("registration.validators.validate_information_responses")
    def test_validate_student_role_information__invalid_id(
        self, mock_validate_responses
    ):
        student = {
            "role": Student.PARENT,
            "information": {
                f"{self.parent_field.id}": "",
                "0": "",
            },
        }
        self.assertRaises(ValidationError, validate_student_role_information, student)
        mock_validate_responses.assert_not_called()

    @patch("registration.validators.validate_information_responses")
    def test_validate_student_role_information__invalid_role(
        self, mock_validate_responses
    ):
        student = {
            "role": Student.PARENT,
            "information": {
                f"{self.parent_field.id}": "",
                f"{self.child_field.id}": "",
            },
        }
        self.assertRaises(ValidationError, validate_student_role_information, student)
        mock_validate_responses.assert_not_called()
