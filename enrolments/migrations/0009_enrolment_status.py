# Generated by Django 3.1.6 on 2021-04-21 00:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("enrolments", "0008_session_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="enrolment",
            name="status",
            field=models.CharField(
                choices=[
                    ("Waiting to enrol", "Waiting to enrol"),
                    ("Registered", "Registered"),
                    ("Confirmed", "Confirmed"),
                    ("Completed", "Completed"),
                    ("No show", "No show"),
                    ("Drop out", "Drop out"),
                    ("Waitlisted", "Waitlisted"),
                ],
                default="Waiting to enrol",
                max_length=16,
            ),
        ),
    ]
