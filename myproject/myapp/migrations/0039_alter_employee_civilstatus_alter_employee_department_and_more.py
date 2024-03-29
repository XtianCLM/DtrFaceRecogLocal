# Generated by Django 4.2.7 on 2023-12-29 02:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0038_employee_empimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='CivilStatus',
            field=models.CharField(default='N/A', max_length=10),
        ),
        migrations.AlterField(
            model_name='employee',
            name='Department',
            field=models.CharField(blank=True, default='N/A', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='EmploymentStatus',
            field=models.CharField(default='Regular', max_length=15),
        ),
        migrations.AlterField(
            model_name='employee',
            name='Gender',
            field=models.CharField(default='Male', max_length=8),
        ),
    ]
