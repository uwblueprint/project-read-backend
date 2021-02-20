from django.test import TestCase
from registration.models import Student
from .validators import validate_attendance
from django.core.exceptions import ValidationError


class ValidatorsTestCase(TestCase):
    def setUp(self):
        Student.objects.bulk_create(
            [
                Student(
                    first_name="Brittany", last_name="Buckets", attendee_type="Parent"
                ),
                Student(first_name="Buckets", last_name="Jr", attendee_type="Child"),
            ]
        )
        self.student_ids = Student.objects.values_list("id")

    def test_attendance_date_format(self):
        obj1 = [{"date": "2021-04-19", "attendees": []}]
        obj2 = [{"date": "2021/04/19", "attendees": []}]
        obj3 = [{"date": "2021-99-99", "attendees": []}]
        self.assertEqual(validate_attendance(obj1), None)
        self.assertRaises(ValidationError, validate_attendance, obj2)
        self.assertRaises(ValidationError, validate_attendance, obj3)

    def test_attendees_exist(self):
        obj1 = [{"date": "2021-04-19", "attendees": self.student_ids}]
        obj2 = [{"date": "2021-04-19", "attendees": [999]}]
        self.assertEqual(validate_attendance(obj1), None)
        self.assertRaises(ValidationError, validate_attendance, obj2)
