# Generated by Django 4.2.7 on 2023-12-28 02:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0036_remove_attendancecount_last_reset_month'),
    ]

    operations = [
        migrations.AddField(
            model_name='branches',
            name='BranchImage',
            field=models.ImageField(blank=True, null=True, upload_to='branch_image/'),
        ),
    ]
