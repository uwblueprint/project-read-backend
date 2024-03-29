from django.db import models
from .validators import (
    validate_family_parent,
    validate_student,
    validate_mc_options,
    validate_interactions,
)
from django.contrib.postgres.fields import ArrayField
from safedelete.models import SafeDeleteModel


class Family(models.Model):
    HOME_NUMBER = "Home"
    CELL_NUMBER = "Cell"
    WORK_NUMBER = "Work"
    NUMBER_PREF_CHOICES = [
        (HOME_NUMBER, "Home"),
        (CELL_NUMBER, "Cell"),
        (WORK_NUMBER, "Work"),
    ]

    parent = models.ForeignKey(
        "Student",
        null=True,
        on_delete=models.PROTECT,
        related_name="represents_family",
        validators=[validate_family_parent],
    )
    email = models.EmailField(blank=True)
    home_number = models.CharField(max_length=128, blank=True, default="")
    cell_number = models.CharField(max_length=128, blank=True, default="")
    work_number = models.CharField(max_length=128, blank=True, default="")
    preferred_number = models.CharField(
        max_length=4, choices=NUMBER_PREF_CHOICES, default="Cell"
    )
    address = models.CharField(max_length=256, blank=True)
    preferred_comms = models.CharField(max_length=128, blank=True)
    notes = models.TextField(blank=True)
    interactions = models.JSONField(
        default=list, validators=[validate_interactions], blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "accounts.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name_plural = "families"

    @property
    def children(self):
        return self.students.filter(role=Student.CHILD)

    @property
    def guests(self):
        return self.students.filter(role=Student.GUEST)

    @property
    def phone_number(self):
        if self.preferred_number == "Cell":
            return self.cell_number
        elif self.preferred_number == "Home":
            return self.home_number
        elif self.preferred_number == "Work":
            return self.work_number

    @property
    def current_enrolment(self):
        return (
            self.enrolments.filter(session__active=True, is_guest=False)
            .order_by("-session__start_date")
            .first()
        )

    def __str__(self):
        if self.parent is not None:
            return f"{self.id} - {self.parent.first_name} {self.parent.last_name} - {self.email}"
        return f"{self.id} - {self.email}"


class Student(SafeDeleteModel):
    PARENT = "Parent"
    CHILD = "Child"
    GUEST = "Guest"
    ROLE_CHOICES = [
        (PARENT, "Parent"),
        (CHILD, "Child"),
        (GUEST, "Guest"),
    ]

    first_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128, blank=True, default="")
    role = models.CharField(max_length=6, choices=ROLE_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    family = models.ForeignKey(
        "Family",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="students",
    )
    information = models.JSONField(default=dict, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name_plural = "students"

    def clean(self):
        validate_student(self)
        return super().clean()


class Field(SafeDeleteModel):
    PARENT = "Parent"
    CHILD = "Child"
    GUEST = "Guest"
    SESSION = "Session"
    ROLE_CHOICES = [
        (PARENT, "Parent"),
        (CHILD, "Child"),
        (GUEST, "Guest"),
        (SESSION, "Session"),
    ]

    TEXT = "Text"
    SELECT = "Select"
    MULTIPLE_SELECT = "Multiple Select"
    QUESTION_CHOICES = [
        (TEXT, "Text"),
        (SELECT, "Select"),
        (MULTIPLE_SELECT, "Multiple Select"),
    ]

    role = models.CharField(max_length=7, choices=ROLE_CHOICES)
    name = models.CharField(max_length=512)
    question = models.CharField(max_length=512, blank=True)
    question_type = models.CharField(max_length=15, choices=QUESTION_CHOICES)
    is_default = models.BooleanField()
    options = ArrayField(
        models.CharField(max_length=64, blank=False),
        default=list,
        validators=[validate_mc_options],
        blank=True,
    )
    order = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.name}"
