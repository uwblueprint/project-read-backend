# Generated by Django 3.1.6 on 2021-08-31 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("registration", "0022_auto_20210824_0030"),
    ]

    operations = [
        migrations.AddField(
            model_name="field",
            name="deleted",
            field=models.DateTimeField(editable=False, null=True),
        ),
    ]
