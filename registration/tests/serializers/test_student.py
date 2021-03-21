from django.core.exceptions import ValidationError
from django.test.testcases import TestCase
from unittest.mock import patch

from registration.models import Student, Field
from registration.serializers import StudentSerializer


class StudentSerializerTestCase(TestCase):
    def setUp(self):
        self.field = Field.objects.create(
            role=Field.PARENT,
            name="Internet Access",
            question="Do you have access to internet",
            question_type=Field.TEXT,
            is_default=True,
            order=1,
        )

        self.student_data = {
            "first_name": "Molly",
            "last_name": "Weasley",
            "information": {f"{self.field.id}": "yes"},
            "role": Student.PARENT,
        }

    @patch("registration.serializers.validate_student_information_role")
    def test_family_detail_serializer_validate(self, mock_validate):
        self.assertTrue(StudentSerializer(data=self.student_data).is_valid())
        mock_validate.assert_called_once()

    @patch(
        "registration.serializers.validate_student_information_role",
        side_effect=ValidationError(""),
    )
    def test_family_detail_serializer_validate__invalid(self, mock_validate):
        self.assertFalse(StudentSerializer(data=self.student_data).is_valid())
        mock_validate.assert_called_once()
