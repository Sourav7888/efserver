# Generated by Django 3.2.8 on 2021-10-23 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_userinfo_user_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='confirmed_user',
            field=models.BooleanField(default=False),
        ),
    ]
