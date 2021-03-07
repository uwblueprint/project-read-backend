from django.db import models
from .validators import (
    validate_family_parent,
    validate_parent_field_name,
    validate_child_field_name,
)


class Family(models.Model):
    parent = models.ForeignKey(
        "Student",
        null=True,
        on_delete=models.PROTECT,
        related_name="represents_family",
        validators=[validate_family_parent],
    )
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=128, blank=True)
    address = models.CharField(max_length=256, blank=True)
    preferred_comms = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "accounts.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        if self.parent is not None:
            return f"{self.id} - {self.parent.first_name} {self.parent.last_name} - {self.email}"
        return f"{self.id} - {self.email}"

    class Meta:
        verbose_name_plural = "families"


class Student(models.Model):
    PARENT = "Parent"
    CHILD = "Child"
    GUEST = "Guest"
    ATTENDEE_CHOICES = [
        (PARENT, "Parent"),
        (CHILD, "Child"),
        (GUEST, "Guest"),
    ]

    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    attendee_type = models.CharField(max_length=6, choices=ATTENDEE_CHOICES)
    family = models.ForeignKey(
        "Family",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    information = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name_plural = "students"


class FamilyInfo(models.Model):
    name = models.CharField(max_length=512, validators=[validate_parent_field_name])
    question = models.CharField(max_length=512)

    def __str__(self):
        return f"{self.name}"


class ChildInfo(models.Model):
    name = models.CharField(max_length=512, validators=[validate_child_field_name])
    question = models.CharField(max_length=512)

    def __str__(self):
        return f"{self.name}"
