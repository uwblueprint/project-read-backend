# Generated by Django 3.1.6 on 2021-06-11 03:34

import django.contrib.postgres.fields
from django.db import migrations, models
import enrolments.validators


# Generated by Django 3.1.6 on 2021-06-06 21:19

import django.contrib.postgres.fields
from django.db import migrations, models
import enrolments.validators


class Migration(migrations.Migration):

    dependencies = [
        ("enrolments", "0013_auto_20210530_2200"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="session",
            name="fields",
        ),
        migrations.AddField(
            model_name="session",
            name="fields",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.IntegerField(),
                default=list,
                size=None,
                validators=[enrolments.validators.validate_fields],
            ),
        ),
    ]
