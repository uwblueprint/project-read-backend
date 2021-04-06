from django.core.exceptions import ValidationError
from django.test import TestCase
from unittest.mock import patch

from ..models import Student


class ValidatorsTestCase(TestCase):
    @patch("registration.models.validate_student")
    def test_validate_information(self, mock_validate):
        parent = Student(
            first_name="Marlin",
            last_name="Fish",
            role=Student.PARENT,
            information={},
        )
        self.assertIsNone(parent.clean())
        mock_validate.assert_called_once_with(parent)

    @patch("registration.models.validate_student", side_effect=ValidationError(""))
    def test_validate_information__invalid(self, mock_validate):
        parent = Student(
            first_name="Marlin",
            last_name="Fish",
            role=Student.PARENT,
            information={},
        )
        self.assertRaises(ValidationError, parent.clean)
        mock_validate.assert_called_once_with(parent)
