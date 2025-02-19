# Generated by Django 3.2.8 on 2022-01-09 03:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0003_alter_userinfo_access_level'),
    ]

    operations = [
        migrations.CreateModel(
            name='WasteCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Waste Categories',
            },
        ),
        migrations.CreateModel(
            name='WasteProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider_name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='WasteData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pickup_date', models.DateField()),
                ('waste_name', models.CharField(max_length=255)),
                ('weight', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('is_recycled', models.BooleanField(default=False)),
                ('facility', models.ForeignKey(blank=True, db_column='facility', null=True, on_delete=django.db.models.deletion.CASCADE, to='core.facility', to_field='facility_name')),
                ('provided_by', models.ForeignKey(db_column='provided_by', on_delete=django.db.models.deletion.CASCADE, to='waste_manager.wasteprovider', to_field='provider_name')),
                ('waste_category', models.ForeignKey(db_column='waste_category', on_delete=django.db.models.deletion.CASCADE, to='waste_manager.wastecategory', to_field='category_name')),
            ],
            options={
                'verbose_name_plural': 'Waste Data',
            },
        ),
        migrations.AddConstraint(
            model_name='wastedata',
            constraint=models.UniqueConstraint(fields=('facility', 'pickup_date', 'waste_name'), name='no_duplicate_waste_data'),
        ),
    ]
