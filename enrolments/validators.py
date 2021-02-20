from datetime import datetime
from django.core.exceptions import ValidationError
from registration.models import Student


def validate_attendance(classObj):
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
    for session in classObj:
        date = session["date"]
        attendees = session["attendees"]
        try:
            datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError(
                "%(date) must be formatted as YYYY-MM-DD and must be a valid date",
                code="invalid",
                params={"date": date},
            )
        if attendees and not Student.objects.filter(pk__in=attendees).exists():
            raise ValidationError(
                "one or more %(attendee)(s) do not exist",
                code="invalid",
                params={"attendee": attendees},
            )
