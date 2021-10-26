# Generated by Django 3.2.8 on 2021-10-25 12:03

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Investigation',
            fields=[
                ('investigation_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('investigation_date', models.DateField()),
                ('investigation_type', models.CharField(choices=[('HC_WT', 'HC_WT'), ('HC_GAS', 'HC_GAS'), ('HC_EL', 'HC_EL')], max_length=6)),
                ('investigation_description', models.TextField(blank=True, null=True)),
                ('investigation_result', models.TextField(blank=True, null=True)),
                ('facility', models.ForeignKey(blank=True, db_column='facility', null=True, on_delete=django.db.models.deletion.CASCADE, to='core.facility', to_field='facility_name')),
                ('investigation_creator', models.ForeignKey(blank=True, db_column='investigation_creator', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='investigation_creator', to='core.userinfo', to_field='user_name')),
                ('investigator', models.ForeignKey(blank=True, db_column='investigator', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='investigator', to='core.userinfo', to_field='user_name')),
            ],
        ),
    ]
