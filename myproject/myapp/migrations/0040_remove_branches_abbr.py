# Generated by Django 4.2.7 on 2024-01-02 06:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0039_alter_employee_civilstatus_alter_employee_department_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='branches',
            name='abbr',
        ),
    ]
