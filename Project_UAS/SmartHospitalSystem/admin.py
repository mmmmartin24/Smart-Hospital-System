from django.contrib import admin
from .models import Sensor_List_int
from .models import Actuator_List

@admin.register(Sensor_List_int)
class DaftarSensorAdmin(admin.ModelAdmin):
    list_display = ('name','Data','timestamp')
    list_filter = ('name','timestamp')
    search_fields = ('name', 'Data')
    ordering = ('-timestamp',)

@admin.register(Sensor_List_int.history.model)
class DaftarSensorHistoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'Data', 'timestamp')
    list_filter = ('name', 'timestamp')
    search_fields = ('name', 'Data')
    ordering = ('-timestamp',)

@admin.register(Actuator_List)
class DaftarSensorAdmin(admin.ModelAdmin):
    list_display = ('name','Data','timestamp')
    list_filter = ('name','timestamp')
    search_fields = ('name', 'Data')
    #date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)

@admin.register(Actuator_List.history.model)
class DaftarSensorHistoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'Data', 'timestamp')
    list_filter = ('name', 'timestamp')
    search_fields = ('name', 'Data')
    ordering = ('-timestamp',)

#bikin supaya bisa view per sensor dan per actuator
