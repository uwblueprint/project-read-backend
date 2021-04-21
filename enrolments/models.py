from django.db import models
from .validators import validate_attendance, validate_enrolment, validate_fields


class Session(models.Model):
    SPRING = "Spring"
    SUMMER = "Summer"
    FALL = "Fall"
    SEASON_CHOICES = [
        (SPRING, "Spring"),
        (SUMMER, "Summer"),
        (FALL, "Fall"),
    ]

    season = models.CharField(max_length=6, choices=SEASON_CHOICES)
    year = models.PositiveSmallIntegerField()
    fields = models.JSONField(default=list, validators=[validate_fields])

    def __str__(self):
        return self.season


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

    attendance = models.JSONField(validators=[validate_attendance])

    class Meta:
        verbose_name_plural = "classes"

    def __str__(self):
        return self.name


class Enrolment(models.Model):
    WAITING_TO_ENROL = "Waiting to enrol"
    REGISTERED = "Registered"
    CONFIRMED = "Confirmed"
    COMLETED = "Completed"
    NO_SHOW = "No show"
    DROP_OUT = "Drop out"
    WAITLISTED = "Waitlisted"
    ENROLMENT_STATUSES = [
        (WAITING_TO_ENROL, "Waiting to enrol"),
        (REGISTERED, "Registered"),
        (CONFIRMED, "Confirmed"),
        (COMLETED, "Completed"),
        (NO_SHOW, "No show"),
        (DROP_OUT, "Drop out"),
        (WAITLISTED, "Waitlisted"),
    ]
    active = models.BooleanField()
    family = models.ForeignKey("registration.Family", on_delete=models.PROTECT)
    session = models.ForeignKey(
        "enrolments.Session",
        null=True,
        on_delete=models.PROTECT,
    )
    preferred_class = models.ForeignKey(
        "enrolments.Class",
        null=True,
        on_delete=models.PROTECT,
        related_name="preferred_enrolment",
    )
    enrolled_class = models.ForeignKey("enrolments.Class", on_delete=models.PROTECT)
    status = models.CharField(max_length=16, choices=ENROLMENT_STATUSES, default=WAITING_TO_ENROL)
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
