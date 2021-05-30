from datetime import datetime
from django.core.exceptions import ValidationError
from registration.models import Student, Field
from django.apps import apps


def validate_students_in_enrolment(enrolment):
    Student = apps.get_model("registration", "Student")
    if (
        len(enrolment.students)
        != Student.objects.filter(
            id__in=enrolment.students, family=enrolment.family
        ).count()
    ):
        raise ValidationError(
            f"Enroled student IDs do not completely match with students under this family"
        )


def validate_class_in_session(class_obj, session):
    if class_obj is not None and class_obj.session != session:
        raise ValidationError(
            f"Class {class_obj.name} is not in session with ID {session.id}"
        )


def validate_enrolment_in_session(session, family):
    Enrolment = apps.get_model("enrolments", "Enrolment")
    family_enrolments_in_session = Enrolment.objects.filter(
        session=session, family=family
    )
    if len(family_enrolments_in_session) > 1:
        raise ValidationError(
            f"Family with ID {family.id} has multiple enrolments per Session with ID {session.id}"
        )


def validate_enrolment(enrolment):
    validate_class_in_session(enrolment.preferred_class, enrolment.session)
    validate_class_in_session(enrolment.enrolled_class, enrolment.session)
    validate_enrolment_in_session(enrolment.session, enrolment.family)


def validate_attendance(class_obj):
    """
    Validates against the attendance column for the Class model.
    The expected structure is:
    [
        {
            "date": "2021-04-19",
            "attendees": [
                // student IDs
                1, 2, 3, 4, 5
            ]
        },
        {
            "date": "2021-04-26",
            "attendees": [
                // student IDs
                1, 2, 3, 4, 5
            ]
        }
    ]
    """

    schema = [{"date": "str", "attendees": ["int"]}]
    if not validate_schema(class_obj, schema):
        raise ValidationError("invalid json structure", code="invalid_schema")
    for session in class_obj:
        date = session["date"]
        attendees = session["attendees"]
        try:
            datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError(
                date + " must be formatted as YYYY-MM-DD and must be a valid date",
                code="invalid_date",
            )
        if attendees and not set(
            Student.objects.filter(pk__in=attendees).values_list("id", flat=True)
        ) == set(attendees):
            raise ValidationError(
                "one or more of the following attendee IDs do not exist: "
                + str(attendees),
                code="invalid_attendee",
            )


def validate_fields(fields_list):
    """
    Validates against the fields column for the Session model.
    The expected structure is:
    [
        // field IDs
        1, 2, 3, 4, 5
    ]
    """
    schema = ["int"]
    if not validate_schema(fields_list, schema):
        raise ValidationError("invalid json structure", code="invalid_schema")
    if fields_list and not set(
        Field.objects.filter(pk__in=fields_list).values_list("id", flat=True)
    ) == set(fields_list):
        raise ValidationError(
            "one or more of the following attendee IDs do not exist: "
            + str(fields_list),
            code="invalid_field",
        )


def validate_schema(json, schema, strict=False):
    """
        schema = {
    ...     "type" : "object",
    ...     "properties" : {
    ...         "price" : {"type" : "number"},
    ...         "name" : {"type" : "string"},
    ...     },
    ... }

        schema = {
            "price": "int",
            "name": "str"
        }
        Basic schema validator that makes sure structure and types match

        :param json: dict - JSON object to validate
        :param schema: dict - The schema the json object must follow.
            Types must be of Python's four primitive types: str, float, int, bool

            Example schema:
                [
                    {
                        "date": "str",
                        "attendees": ["int"]
                    }
                ]
        :param strict: boolean - If true, no other fields outside of the schema are allowed.
        :return: boolean as to whether json follows schema

        NOTE: All elements of array must be of the same structure
    """
    if isinstance(json, list):
        if not isinstance(schema, list):
            return False
        return all(
            [validate_schema(json[i], schema[0], strict) for i in range(len(json))]
        )
    if isinstance(json, dict):
        if not isinstance(schema, dict):
            return False
        keys_left = set(schema.keys())
        for key, val in json.items():
            if key not in schema:
                if strict:
                    return False
                continue
            if not validate_schema(val, schema[key], strict):
                return False
            keys_left.remove(key)
        return not keys_left
    if schema == "str":
        return isinstance(json, str)
    if schema == "int":
        return isinstance(json, int)
    if schema == "bool":
        return isinstance(json, bool)
    if schema == "float":
        return isinstance(json, float)
    return False
