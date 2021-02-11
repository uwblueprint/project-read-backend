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
