from django.db import models
from .validators import (
    validate_attendance,
    validate_enrolment,
    validate_fields,
)
from django.contrib.postgres.fields import ArrayField


class Session(models.Model):
    name = models.CharField(max_length=128, default="")
    start_date = models.DateField(null=True)
    active = models.BooleanField(default=False)

    fields = ArrayField(
        models.IntegerField(), default=list, validators=[validate_fields]
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name


class Class(models.Model):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"
    DAYS_OF_THE_WEEK = [
        (MONDAY, "Monday"),
        (TUESDAY, "Tuesday"),
        (WEDNESDAY, "Wednesday"),
        (THURSDAY, "Thursday"),
        (FRIDAY, "Friday"),
        (SATURDAY, "Saturday"),
        (SUNDAY, "Sunday"),
    ]
    name = models.CharField(max_length=128)
    session = models.ForeignKey(
        "Session",
        related_name="classes",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    facilitator = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    attendance = models.JSONField(
        default=list,
        blank=True,
        validators=[validate_attendance],
    )
    colour = models.CharField(
        max_length=6,
        default="FFFFFF",
        blank=True,
    )
    days = ArrayField(
        models.CharField(max_length=9, blank=True, choices=DAYS_OF_THE_WEEK),
        default=list,
        blank=True,
    )
    location = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name_plural = "classes"

    def __str__(self):
        return self.name


class Enrolment(models.Model):
    SIGNED_UP = "Signed up"
    REGISTERED = "Registered"
    CLASS_ALLOCATED = "Class allocated"
    COMPLETED = "Completed"
    NO_SHOW = "No show"
    DROP_OUT = "Drop out"
    WAITLISTED = "Waitlisted"
    ENROLMENT_STATUSES = [
        (SIGNED_UP, "Signed up"),
        (REGISTERED, "Registered"),
        (CLASS_ALLOCATED, "Class allocated"),
        (COMPLETED, "Completed"),
        (NO_SHOW, "No show"),
        (DROP_OUT, "Drop out"),
        (WAITLISTED, "Waitlisted"),
    ]
    family = models.ForeignKey(
        "registration.Family", on_delete=models.PROTECT, related_name="enrolments"
    )
    students = ArrayField(
        models.PositiveIntegerField(),
        default=list,
    )
    session = models.ForeignKey(
        "enrolments.Session",
        null=True,
        on_delete=models.PROTECT,
        related_name="enrolments",
    )
    preferred_class = models.ForeignKey(
        "enrolments.Class",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    enrolled_class = models.ForeignKey(
        "enrolments.Class",
        on_delete=models.PROTECT,
        related_name="enrolments",
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=16, choices=ENROLMENT_STATUSES, default=SIGNED_UP
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "accounts.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    is_guest = models.BooleanField(default=False)

    def clean(self):
        validate_enrolment(self)
        return super().clean()
