from django.test import TestCase
from ..models import Student
from ..validators import validate_family_parent
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
