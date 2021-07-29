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
    fields = ArrayField(
        models.IntegerField(), default=list, validators=[validate_fields]
    )

    def __str__(self):
        return self.name


class Class(models.Model):
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
    active = models.BooleanField()
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

    def clean(self):
        validate_enrolment(self)
        return super().clean()
