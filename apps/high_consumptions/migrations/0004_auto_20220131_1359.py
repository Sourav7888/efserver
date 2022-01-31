# Generated by Django 3.2.8 on 2022-01-31 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('high_consumptions', '0003_hc_hc_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hc',
            name='cost_increase',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=7),
        ),
        migrations.AlterField(
            model_name='hc',
            name='usage_increase',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=7),
        ),
    ]
