# Generated by Django 4.2.7 on 2023-12-06 01:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_remove_temporaryattendance_student'),
    ]

    operations = [
        migrations.AddField(
            model_name='temporaryattendance',
            name='student_code',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.student', to_field='code'),
        ),
    ]
