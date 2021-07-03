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
    try:
        if (
            len(information)
            != Field.objects.filter(id__in=information.keys(), role=role).count()
        ):
            raise ValidationError(
                f"One of the provided IDs is not a valid {role} field ID"
            )
        validate_information_responses(information.values())
    except ValidationError as ve:
        raise ve
    except:
        raise ValidationError("Invalid information JSON")


def validate_student(student):
    validate_student_information_role(student.information, student.role)


def validate_mc_options(field):
    if not all(isinstance(option, str) for option in field.options):
        raise ValidationError("One of the provided options is not a string")


def validate_client_interaction(interaction):
    from enrolments.validators import validate_schema

    INTERACTION_SCHEMA = {
        "type": "str",
        "date": "str",
        "user_id": "int",
        "user_email": "str",
    }
    validate_schema(interaction, INTERACTION_SCHEMA)
    User = apps.get_model("accounts", "User")
    try:
        User.objects.get(id=interaction["user_id"])
    except User.DoesNotExist as dne_error:
        raise dne_error
    except:
        raise ValidationError("Invalid interaction JSON")


def validate_interactions(interactions):
    for interaction in interactions.values():
        validate_client_interaction(interaction)
