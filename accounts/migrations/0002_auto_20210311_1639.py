# Generated by Django 3.1.6 on 2021-03-11 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={},
        ),
        migrations.AddField(
            model_name="user",
            name="firebase_uid",
            field=models.CharField(default="", max_length=128),
            preserve_default=False,
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(
                fields=["firebase_uid"], name="accounts_us_firebas_e46fff_idx"
            ),
        ),
    ]
