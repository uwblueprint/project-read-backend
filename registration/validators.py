from django.apps import apps
from django.core.exceptions import ValidationError


def validate_family_parent(student_id):
    Student = apps.get_model("registration", "Student")
    student = Student.objects.get(id=student_id)
    if student.role != Student.PARENT:
        raise ValidationError(
            f"{student.first_name} {student.last_name} is a {student.role}, not a {Student.PARENT}"
        )


def validate_information(information):
    Field = apps.get_model("registration", "Field")
    if len(information) != Field.objects.filter(id__in=information.keys()).count():
        raise ValidationError("One of the provided IDs is not a valid field ID")
    for value in information.values():
        if not isinstance(value, str):
            raise ValidationError("One of the provided responses is not a string")


def validate_student_information(students):
    Field = apps.get_model("registration", "Field")
    for student in students:
        information = student.get("information", {})
        role = student["role"]
        if (
            len(information)
            != Field.objects.filter(id__in=information.keys(), role=role).count()
        ):
            raise ValidationError(
                f"One of the provided IDs is not a valid {role} field ID"
            )
