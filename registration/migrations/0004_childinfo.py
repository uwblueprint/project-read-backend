# Generated by Django 3.1.6 on 2021-03-03 01:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("registration", "0003_familyinfo"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChildInfo",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=512)),
                ("question", models.CharField(max_length=512)),
                ("active", models.BooleanField()),
            ],
        ),
    ]
