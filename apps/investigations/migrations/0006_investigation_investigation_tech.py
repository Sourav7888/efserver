# Generated by Django 3.2.8 on 2022-03-15 18:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20220205_2044'),
        ('investigations', '0005_auto_20220315_0346'),
    ]

    operations = [
        migrations.AddField(
            model_name='investigation',
            name='investigation_tech',
            field=models.ForeignKey(blank=True, db_column='investigation_tech', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='investigation_tech', to='core.userinfo', to_field='user_unique_id'),
        ),
    ]
