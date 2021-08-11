# Generated by Django 3.1.6 on 2021-08-10 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0017_auto_20210731_1654'),
    ]

    operations = [
        migrations.AlterField(
            model_name='field',
            name='question',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name='field',
            name='question_type',
            field=models.CharField(choices=[('Text', 'Text'), ('Select', 'Select'), ('Multiple Select', 'Multiple Select')], max_length=15),
        ),
    ]
