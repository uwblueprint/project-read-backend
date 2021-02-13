from django.db import models


class Class(models.Model):
    name = models.CharField(max_length=128)
    # session = models.ForeignKey()
    # facilitator = models.ForeignKey()


def __str__(self):
    return self.name
