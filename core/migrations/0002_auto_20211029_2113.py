# Generated by Django 3.2.8 on 2021-10-29 21:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userinfo',
            name='access_division_energy',
        ),
        migrations.RemoveField(
            model_name='userinfo',
            name='access_division_project',
        ),
        migrations.RemoveField(
            model_name='userinfo',
            name='access_facility_energy',
        ),
        migrations.RemoveField(
            model_name='userinfo',
            name='access_facility_project',
        ),
    ]
