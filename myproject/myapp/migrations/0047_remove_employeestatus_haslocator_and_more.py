# Generated by Django 4.2.7 on 2024-01-04 03:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0046_alter_dailyrecord_totallateness'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employeestatus',
            name='HasLocator',
        ),
        migrations.RemoveField(
            model_name='employeestatus',
            name='HasTripTicket',
        ),
        migrations.RemoveField(
            model_name='employeestatus',
            name='OnLeave',
        ),
        migrations.RemoveField(
            model_name='employeestatus',
            name='Remarks',
        ),
        migrations.RemoveField(
            model_name='employeestatus',
            name='StatusDate',
        ),
        migrations.AddField(
            model_name='employeestatus',
            name='LateCount',
            field=models.CharField(default='0', max_length=5),
        ),
        migrations.AddField(
            model_name='employeestatus',
            name='UndertimeCount',
            field=models.CharField(default='0', max_length=5),
        ),
    ]
