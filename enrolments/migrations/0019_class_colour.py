# Generated by Django 3.1.6 on 2021-07-30 04:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrolments', '0018_auto_20210730_0018'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='colour',
            field=models.CharField(blank=True, default='FFFFFF', max_length=6),
        ),
    ]
