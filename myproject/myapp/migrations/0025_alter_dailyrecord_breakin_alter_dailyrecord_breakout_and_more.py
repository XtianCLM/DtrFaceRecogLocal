# Generated by Django 4.2.7 on 2023-12-21 01:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0024_employee_approveot'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyrecord',
            name='breakin',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='dailyrecord',
            name='breakout',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='dailyrecord',
            name='timein',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='dailyrecord',
            name='timeout',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
