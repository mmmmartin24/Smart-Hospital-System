# Generated by Django 4.2.7 on 2023-11-16 06:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SmartHospitalSystem', '0008_remove_historicalsensor_list_int_details_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='actuator_list',
            name='activation_condition',
        ),
        migrations.RemoveField(
            model_name='actuator_list',
            name='threshold',
        ),
        migrations.RemoveField(
            model_name='historicalactuator_list',
            name='activation_condition',
        ),
        migrations.RemoveField(
            model_name='historicalactuator_list',
            name='threshold',
        ),
    ]
