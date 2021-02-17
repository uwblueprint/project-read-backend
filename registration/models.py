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
