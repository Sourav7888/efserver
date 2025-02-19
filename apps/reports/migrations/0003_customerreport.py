# Generated by Django 3.2.8 on 2022-02-28 01:14

import apps.reports.storages_backends
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20220205_2044'),
        ('reports', '0002_alter_report_created_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_name', models.CharField(max_length=255)),
                ('report_description', models.TextField(blank=True, null=True)),
                ('report_file', models.FileField(blank=True, null=True, storage=apps.reports.storages_backends.ReportsDocs(), upload_to='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(blank=True, db_column='customer', null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.customer', to_field='customer_name')),
            ],
        ),
    ]
