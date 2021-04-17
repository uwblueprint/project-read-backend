# Generated by Django 3.1.6 on 2021-03-24 00:30

from django.db import migrations, models
import enrolments.validators


class Migration(migrations.Migration):

    dependencies = [
        ("enrolments", "0007_merge_20210320_1853"),
    ]

    operations = [
        migrations.AddField(
            model_name="session",
            name="fields",
            field=models.JSONField(
                default=list, validators=[enrolments.validators.validate_fields]
            ),
        ),
    ]