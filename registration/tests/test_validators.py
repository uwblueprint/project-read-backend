from django.test import TestCase
from ..constants import family_detail_constant_fields, student_detail_constant_fields
from ..models import Student
from ..validators import (
    validate_family_parent,
    validate_parent_field_name,
    validate_child_field_name,
)
from django.core.exceptions import ValidationError


class ValidatorsTestCase(TestCase):
    def setUp(self):
        self.parent = Student.objects.create(
            first_name="Merlin", last_name="Fish", attendee_type="Parent"
        )
        self.child = Student.objects.create(
            first_name="Nemo", last_name="Fish", attendee_type="Child"
        )

    def test_family_parent(self):
        self.assertIsNone(validate_family_parent(self.parent.id))
        self.assertRaises(ValidationError, validate_family_parent, self.child.id)

    def validate_parent_field_name(self):
        self.assertIsNone(validate_parent_field_name, "Internet Access"),
        for field in family_detail_constant_fields:
            self.assertRaises(ValidationError, validate_parent_field_name, field)

    def validate_child_field_name(self):
        self.assertIsNone(validate_child_field_name, "Favourite Colour"),
        for field in student_detail_constant_fields:
            self.assertRaises(ValidationError, validate_child_field_name, field)
