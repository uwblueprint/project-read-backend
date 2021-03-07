from django.apps import apps
from django.core.exceptions import ValidationError

from .constants import family_detail_constant_fields, student_detail_constant_fields


def validate_family_parent(student_id):
    Student = apps.get_model("registration", "Student")
    student = Student.objects.get(id=student_id)
    if student.attendee_type != Student.PARENT:
        raise ValidationError(
            f"{student.first_name} {student.last_name} is a {student.attendee_type}, not a {Student.PARENT}"
        )


def validate_parent_field_name(name):
    if name in family_detail_constant_fields.union(student_detail_constant_fields):
        raise ValidationError(
            f"This field name is protected, please choose another one"
        )


def validate_child_field_name(name):
    if name in student_detail_constant_fields:
        raise ValidationError(
            f"This field name is protected, please choose another one"
        )
