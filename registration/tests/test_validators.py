from django.test import TestCase
from ..models import Student, Field
from ..validators import (
    validate_family_parent,
    validate_information,
    validate_student_information,
)
from django.core.exceptions import ValidationError


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

    def test_validate_information(self):
        information = {f"{self.parent_field.id}": "Yes"}
        self.assertIsNone(validate_information(information))

    def test_validate_information__invalid(self):
        information = {f"0": "Yes"}
        self.assertRaises(ValidationError, validate_information, information)

    def test_validate_student_information(self):
        students = [
            {
                "role": Student.PARENT,
                "information": {
                    f"{self.parent_field.id}": "",
                },
            },
            {
                "role": Student.CHILD,
                "information": {
                    f"{self.child_field.id}": "",
                },
            },
            {
                "role": Student.GUEST,
                "information": {
                    f"{self.guest_field.id}": "",
                },
            },
        ]
        self.assertIsNone(validate_student_information(students))

    def test_validate_student_information__invalid_id(self):
        students = [
            {
                "role": Student.PARENT,
                "information": {
                    f"{self.parent_field.id}": "",
                    "0": "",
                },
            }
        ]
        self.assertRaises(ValidationError, validate_student_information, students)

    def test_validate_student_information__invalid_role(self):
        students = [
            {
                "role": Student.PARENT,
                "information": {
                    f"{self.parent_field.id}": "",
                    f"{self.child_field.id}": "",
                },
            }
        ]
        self.assertRaises(ValidationError, validate_student_information, students)
