# Generated by Django 4.2.7 on 2023-11-23 10:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SmartHospitalSystem', '0011_remove_actuator_list_activation_condition_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='actuator_list',
            name='sensor_name',
        ),
        migrations.RemoveField(
            model_name='historicalactuator_list',
            name='sensor_name',
        ),
    ]