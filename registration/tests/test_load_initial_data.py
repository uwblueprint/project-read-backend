from django.core.management import call_command
from django.test import TestCase

from ..models import Family, Field, Student


class LoadInitialDataTestCase(TestCase):
    def setUp(self):
        # Create objects to ensure they're deleted by the management command
        Family.objects.create()
        Student.objects.bulk_create(
            [
                Student(first_name="Marlin", last_name="Fish", role=Student.PARENT),
                Student(first_name="Nemo", last_name="Fish", role=Student.CHILD),
                Student(first_name="Dory", last_name="Fish", role=Student.GUEST),
            ]
        )
        Field.objects.bulk_create(
            [
                Field(
                    role=Field.PARENT,
                    name="DOB",
                    question="What's your date of birth?",
                    question_type=Field.TEXT,
                    is_default=True,
                    order=1,
                ),
                Field(
                    role=Field.CHILD,
                    name="Allergies",
                    question="Do they have any allergies?",
                    question_type=Field.MULTIPLE_CHOICE,
                    is_default=True,
                    order=1,
                ),
                Field(
                    role=Field.GUEST,
                    name="Relationship",
                    question="What's their relationship to your family?",
                    question_type=Field.MULTIPLE_CHOICE,
                    is_default=True,
                    order=1,
                ),
            ]
        )
        self.num_fields = 12

    def test_load_initial_data(self):
        num_families = 30
        call_command(
            "load_initial_data",
            num_families=num_families,
        )
        self.assertEqual(Field.objects.all().count(), self.num_fields)
        self.assertEqual(Family.objects.all().count(), num_families)
        self.assertEqual(
            Student.objects.filter(role=Student.PARENT).count(), num_families
        )
        self.assertGreaterEqual(
            Student.objects.filter(role=Student.CHILD).count(), num_families
        )
        self.assertGreaterEqual(Student.objects.filter(role=Student.GUEST).count(), 1)
