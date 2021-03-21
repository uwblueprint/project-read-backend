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
    for response in responses:
        if not isinstance(response, str):
            raise ValidationError("One of the provided responses is not a string")


def validate_information(information):
    Field = apps.get_model("registration", "Field")
    if len(information) != Field.objects.filter(id__in=information.keys()).count():
        raise ValidationError("One of the provided IDs is not a valid field ID")
    validate_information_responses(information.values())


def validate_students_role_information(students_data):
    Field = apps.get_model("registration", "Field")
    for student in students_data:
        information = student.get("information", {})
        role = student["role"]
        if (
            len(information)
            != Field.objects.filter(id__in=information.keys(), role=role).count()
        ):
            raise ValidationError(
                f"One of the provided IDs is not a valid {role} field ID"
            )
        validate_information_responses(information.values())


def validate_student_role_information(student_data):
    Field = apps.get_model("registration", "Field")

    information = student_data.get("information", {})
    role = student_data["role"]
    if (
        len(information)
        != Field.objects.filter(id__in=information.keys(), role=role).count()
    ):
        raise ValidationError(f"One of the provided IDs is not a valid {role} field ID")
    validate_information_responses(information.values())
