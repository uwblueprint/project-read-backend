# Generated by Django 3.1.6 on 2021-08-21 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("registration", "0019_auto_20210818_0347"),
    ]

    operations = [
        migrations.AlterField(
            model_name="student",
            name="last_name",
            field=models.CharField(max_length=128, null=True),
        ),
    ]
