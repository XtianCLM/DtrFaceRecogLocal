# Generated by Django 4.2.7 on 2023-12-27 07:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0035_attendancecount_last_reset_month'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendancecount',
            name='last_reset_month',
        ),
    ]
