# Generated by Django 4.2.6 on 2023-11-15 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SmartHospitalSystem', '0005_historicalsensor_list_int_details_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actuator_list',
            name='sensor_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='historicalactuator_list',
            name='sensor_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]