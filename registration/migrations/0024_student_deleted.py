# Generated by Django 3.1.6 on 2021-09-15 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("registration", "0023_field_deleted"),
    ]

    operations = [
        migrations.AddField(
            model_name="student",
            name="deleted",
            field=models.DateTimeField(editable=False, null=True),
        ),
    ]