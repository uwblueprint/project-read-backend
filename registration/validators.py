from django.apps import apps
from django.core.exceptions import ValidationError


def validate_family_parent(student_id):
    Student = apps.get_model("registration", "Student")
    student = Student.objects.get(id=student_id)
    if student.role != Student.PARENT:
        raise ValidationError(
            f"{student.first_name} {student.last_name} is a {student.role}, not a {Student.PARENT}"
        )


def validate_information_responses(responses):
    if not all(isinstance(response, str) for response in responses):
        raise ValidationError("One of the provided responses is not a string")


def validate_student_information_role(information, role):
    Field = apps.get_model("registration", "Field")
    if (
        len(information)
        != Field.objects.filter(id__in=information.keys(), role=role).count()
    ):
        raise ValidationError(f"One of the provided IDs is not a valid {role} field ID")
    validate_information_responses(information.values())


def validate_student(student):
    validate_student_information_role(student.information, student.role)
