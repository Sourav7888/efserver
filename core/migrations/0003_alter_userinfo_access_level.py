# Generated by Django 3.2.8 on 2021-10-30 02:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20211029_2113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='access_level',
            field=models.CharField(choices=[('ALL', 'ALL'), ('RESTRICTED', 'RESTRICTED'), ('ENERFROG_STAFF', 'ENERFROG_STAFF')], default='RESTRICTED', max_length=14),
        ),
    ]
