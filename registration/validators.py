from django.apps import apps
from django.core.exceptions import ValidationError


def validate_family_parent(student_id):
    Student = apps.get_model("registration", "Student")
    student = Student.objects.get(id=student_id)
    if student.attendee_type != Student.PARENT:
        raise ValidationError(
            f"{student.first_name} {student.last_name} is a {student.attendee_type}, not a {Student.PARENT}"
        )
