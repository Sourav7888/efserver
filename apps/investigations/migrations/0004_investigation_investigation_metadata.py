# Generated by Django 3.2.8 on 2022-02-22 04:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investigations', '0003_investigationauthorization'),
    ]

    operations = [
        migrations.AddField(
            model_name='investigation',
            name='investigation_metadata',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
