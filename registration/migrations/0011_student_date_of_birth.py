# Generated by Django 3.1.6 on 2021-05-28 00:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("registration", "0010_auto_20210403_2021"),
    ]

    operations = [
        migrations.AddField(
            model_name="student",
            name="date_of_birth",
            field=models.DateField(null=True),
        ),
    ]
