# Generated by Django 4.2.7 on 2024-01-23 02:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0060_employeestatus_dailyrecord'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employeestatus',
            name='DailyRecord',
        ),
    ]
