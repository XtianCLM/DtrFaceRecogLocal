# Generated by Django 4.2.7 on 2023-11-21 03:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ArchiveAttendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('timein', models.CharField(blank=True, max_length=8, null=True)),
                ('timeout', models.CharField(blank=True, max_length=8, null=True)),
                ('breakout', models.CharField(blank=True, max_length=8, null=True)),
                ('breakin', models.CharField(blank=True, max_length=8, null=True)),
            ],
            options={
                'db_table': 'archive',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=15, unique=True)),
                ('firstname', models.CharField(max_length=100)),
                ('middlename', models.CharField(max_length=100)),
                ('lastname', models.CharField(max_length=100)),
                ('branch', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='TemporaryAttendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('timein', models.CharField(blank=True, max_length=8, null=True)),
                ('timeout', models.CharField(blank=True, max_length=8, null=True)),
                ('breakout', models.CharField(blank=True, max_length=8, null=True)),
                ('breakin', models.CharField(blank=True, max_length=8, null=True)),
            ],
            options={
                'db_table': 'temporary',
            },
        ),
    ]
