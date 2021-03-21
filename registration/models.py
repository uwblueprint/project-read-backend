from django.db import models
from .validators import validate_family_parent, validate_student


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

    class Meta:
        verbose_name_plural = "families"

    @property
    def children(self):
        return self.students.filter(role=Student.CHILD)

    @property
    def guests(self):
        return self.students.filter(role=Student.GUEST)

    def __str__(self):
        if self.parent is not None:
            return f"{self.id} - {self.parent.first_name} {self.parent.last_name} - {self.email}"
        return f"{self.id} - {self.email}"


class Student(models.Model):
    PARENT = "Parent"
    CHILD = "Child"
    GUEST = "Guest"
    ROLE_CHOICES = [
        (PARENT, "Parent"),
        (CHILD, "Child"),
        (GUEST, "Guest"),
    ]

    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    role = models.CharField(max_length=6, choices=ROLE_CHOICES)
    family = models.ForeignKey(
        "Family",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="students",
    )
    information = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name_plural = "students"

    def clean(self):
        validate_student(self)
        return super().clean()


class Field(models.Model):
    PARENT = "Parent"
    CHILD = "Child"
    GUEST = "Guest"
    TEXT = "Text"
    MULTIPLE_CHOICE = "Multiple Choice"
    ROLE_CHOICES = [
        (PARENT, "Parent"),
        (CHILD, "Child"),
        (GUEST, "Guest"),
    ]
    QUESTION_CHOICES = [(TEXT, "Text"), (MULTIPLE_CHOICE, "Multiple Choice")]
    role = models.CharField(max_length=6, choices=ROLE_CHOICES)
    name = models.CharField(max_length=512)
    question = models.CharField(max_length=512)
    question_type = models.CharField(max_length=15, choices=QUESTION_CHOICES)
    is_default = models.BooleanField()
    order = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.name}"
