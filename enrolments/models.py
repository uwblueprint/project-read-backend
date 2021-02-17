from django.db import models

# Create your models here.

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

    def __str__(self):
        return self.season


class Class(models.Model):
    name = models.CharField(max_length=128)
    # session = models.ForeignKey()
    # facilitator = models.ForeignKey()

    def __str__(self):
        return self.name

