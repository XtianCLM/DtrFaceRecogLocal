# Generated by Django 4.2.7 on 2024-02-19 02:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0069_remove_dailyrecord_memo_attendancecount_memo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyrecord',
            name='remarks',
            field=models.CharField(default='None', max_length=100),
        ),
        migrations.AlterField(
            model_name='requestform',
            name='date',
            field=models.DateField(default=datetime.date(2024, 2, 19)),
        ),
    ]
