from django.core.exceptions import ValidationError
from django.test import TestCase
from unittest.mock import patch

from ..models import Student, Field
from accounts.models import User
from .. import validators


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
            question_type=Field.SELECT,
            is_default=True,
            options=["Yes", "No"],
            order=1,
        )
        self.guest_field = Field.objects.create(
            role=Field.GUEST,
            name="Relationship",
            question="What's their relationship to your family?",
            question_type=Field.SELECT,
            is_default=True,
            order=1,
        )
        self.session_field = Field.objects.create(
            role=Field.SESSION,
            name="Ontario Works",
            question="Ontario Works?",
            question_type=Field.SELECT,
            is_default=True,
            order=1,
        )
        self.test_user = User.objects.create(
            email="user@test.com",
        )

    def test_validate_family_parent(self):
        self.assertIsNone(validators.validate_family_parent(self.parent.id))
        self.assertRaises(
            ValidationError, validators.validate_family_parent, self.child.id
        )

    def test_validate_information_responses(self):
        responses = ["a", "b", "c"]
        self.assertIsNone(validators.validate_information_responses(responses))

    def test_validate_information_responses__invalid(self):
        responses = [["a"], "b", "c"]
        self.assertRaises(
            ValidationError, validators.validate_information_responses, responses
        )

    @patch("registration.validators.validate_information_responses")
    def test_validate_student_information_role(self, mock_validate):
        student = {
            "role": Student.PARENT,
            "information": {
                f"{self.parent_field.id}": "value",
            },
        }
        self.assertIsNone(
            validators.validate_student_information_role(
                student["information"],
                student["role"],
            )
        )
        mock_validate.assert_called_once()
        self.assertListEqual(
            list(mock_validate.call_args.args[0]),
            list(student["information"].values()),
        )

    @patch("registration.validators.validate_information_responses")
    def test_validate_student_information_role__session_field(self, mock_validate):
        student = {
            "role": Student.PARENT,
            "information": {
                f"{self.parent_field.id}": "value",
                f"{self.session_field.id}": "value",
            },
        }
        self.assertIsNone(
            validators.validate_student_information_role(
                student["information"],
                student["role"],
            )
        )
        mock_validate.assert_called_once()
        self.assertListEqual(
            list(mock_validate.call_args.args[0]),
            list(student["information"].values()),
        )

    @patch("registration.validators.validate_information_responses")
    def test_validate_student_information_role__invalid_id(self, mock_validate):
        student = {
            "role": Student.PARENT,
            "information": {
                f"{self.parent_field.id}": "",
                "0": "",
            },
        }
        self.assertRaises(
            ValidationError,
            validators.validate_student_information_role,
            student["information"],
            student["role"],
        )
        mock_validate.assert_not_called()

    @patch("registration.validators.validate_information_responses")
    def test_validate_student_information_role__invalid_role(self, mock_validate):
        student = {
            "role": Student.PARENT,
            "information": {
                f"{self.parent_field.id}": "",
                f"{self.child_field.id}": "",
            },
        }
        self.assertRaises(
            ValidationError,
            validators.validate_student_information_role,
            student["information"],
            student["role"],
        )
        mock_validate.assert_not_called()

    @patch(
        "registration.validators.validate_information_responses",
        side_effect=ValidationError(""),
    )
    def test_validate_student_information_role__invalid_responses(self, mock_validate):
        student = {
            "role": Student.PARENT,
            "information": {
                f"{self.parent_field.id}": ["value"],
            },
        }
        self.assertRaises(
            ValidationError,
            validators.validate_student_information_role,
            student["information"],
            student["role"],
        )
        self.assertListEqual(
            list(mock_validate.call_args.args[0]),
            list(student["information"].values()),
        )

    @patch("registration.validators.validate_student_information_role")
    def test_validate_student(self, mock_validate):
        student = Student(role=Student.PARENT, information={})
        self.assertIsNone(validators.validate_student(student))
        mock_validate.assert_called_once_with(student.information, student.role)

    @patch(
        "registration.validators.validate_student_information_role",
        side_effect=ValidationError(""),
    )
    def test_validate_student__invalid(self, mock_validate):
        student = Student(role=Student.PARENT, information={})
        self.assertRaises(
            ValidationError,
            validators.validate_student,
            student,
        )
        mock_validate.assert_called_once_with(student.information, student.role)

    def test_validate_mc_options(self):
        test_field = self.child_field
        self.assertIsNone(validators.validate_mc_options(test_field.options))
        test_field.options.append(1)
        self.assertRaises(
            ValidationError, validators.validate_mc_options, test_field.options
        )

    def test_validate_client_interaction(self):
        interaction_valid = {
            "type": "Phone Call",
            "date": "2012-04-04",
            "user_id": self.test_user.id,
        }
        interaction_invalid_schema = {
            "date": "2012-04-04",
            "user_id": self.test_user.id,
        }
        interaction_invalid_user = {
            "type": "Phone Call",
            "date": "2012-04-04",
            "user_id": self.test_user.id + 1,
        }
        self.assertIsNone(validators.validate_client_interaction(interaction_valid))
        self.assertFalse(
            validators.validate_client_interaction(interaction_invalid_schema)
        )
        self.assertRaises(
            User.DoesNotExist,
            validators.validate_client_interaction,
            interaction_invalid_user,
        )
