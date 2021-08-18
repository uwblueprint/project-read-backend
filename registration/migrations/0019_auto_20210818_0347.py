# Generated by Django 3.1.6 on 2021-08-18 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("registration", "0018_auto_20210810_2256"),
    ]

    operations = [
        migrations.AddField(
            model_name="field",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="field",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name="student",
            name="last_name",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
