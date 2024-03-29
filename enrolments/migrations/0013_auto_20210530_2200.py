# Generated by Django 3.1.6 on 2021-05-30 22:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("registration", "0013_auto_20210530_2200"),
        ("enrolments", "0012_session_start_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="enrolment",
            name="family",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="enrolments",
                to="registration.family",
            ),
        ),
        migrations.AlterField(
            model_name="session",
            name="start_date",
            field=models.DateField(null=True),
        ),
    ]
