from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts.managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    firebase_uid = models.CharField(max_length=128)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        indexes = [
            models.Index(fields=['firebase_uid'])
        ]

    def __str__(self):
        return self.email

    @property
    def is_authenticated(self):
        return True
