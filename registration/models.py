from django.db import models


class Family(models.Model):
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
        related_name="students",
    )
    information = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name_plural = "students"


class FamilyInfo(models.Model):
    name = models.CharField(max_length=512)
    question = models.CharField(max_length=512)
    active = models.BooleanField()

    def __str__(self):
        return f"{self.name}"


class ChildInfo(models.Model):
    name = models.CharField(max_length=512)
    question = models.CharField(max_length=512)
    active = models.BooleanField()

    def __str__(self):
        return f"{self.name}"
