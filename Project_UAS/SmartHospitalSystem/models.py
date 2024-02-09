from django.db import models
from simple_history.models import HistoricalRecords
from django.contrib.postgres.fields import JSONField
from simple_history.models import HistoricalRecords

class Sensor_List_int(models.Model):
    name =  models.CharField(max_length=100)
    Data = models.FloatField()
    unit = models.CharField(max_length=50,default= '-')
    timestamp = models.CharField(max_length=100)
    history = HistoricalRecords()


class Actuator_List(models.Model):
    name = models.CharField(max_length=100)
    Data = models.FloatField()
    timestamp = models.CharField(max_length=100)
    history = HistoricalRecords()


    def __str__(self):
        return self.name
