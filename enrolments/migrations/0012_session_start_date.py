# Generated by Django 3.1.6 on 2021-05-08 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("enrolments", "0011_merge_20210502_0144"),
    ]

    operations = [
        migrations.AddField(
            model_name="session",
            name="start_date",
            field=models.DateTimeField(null=True),
        ),
    ]