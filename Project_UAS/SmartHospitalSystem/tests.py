<!DOCTYPE html>
<html lang="en">
<head>
    <!-- your head content -->
</head>
<body>
    <h1>SMART HOSPITAL SYSTEM</h1>

    <h2>Sensors and Actuators</h2>

    <!-- First Table -->
    <h3>Table 1</h3>
    <table border="1">
        <!-- Table header for both sensors and actuators -->
        <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Data</th>
            <td>Unit</td>
            <th>Timestamp</th>
            <th>Details</th>
        </tr>
    
        <!-- Loop through sensors and actuators and display data for Table 1 -->
        {% for sensor in sensors_table1 %}
            <tr>
                <td>{{ sensor.name }}</td>
                <td>Sensor</td>
                <td>{{ sensor.Data|floatformat:2 }}</td>
                <td>{{ sensor.unit }}</td>
                <td>{{ sensor.timestamp }}</td>
                <td>{{ sensor.details }}</td>
            </tr>
        {% endfor %}

        {% for actuator in actuators_table1 %}
            <tr>
                <td>{{ actuator.name }}</td>
                <td>Actuator</td>
                <td>{{ actuator.Data }}</td>
                <td></td> <!-- You might not have a unit for actuators, adjust as needed -->
                <td>{{ actuator.timestamp }}</td>
                <td></td> <!-- You might not have details for actuators, adjust as needed -->
            </tr>
        {% endfor %}
    </table>

    <!-- Second Table -->
    <h3>Table 2</h3>
    <table border="1">
        <!-- Table header for both sensors and actuators -->
        <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Data</th>
            <td>Unit</td>
            <th>Timestamp</th>
            <th>Details</th>
        </tr>
    
        <!-- Loop through sensors and actuators and display data for Table 2 -->
        {% for sensor in sensors_table2 %}
            <tr>
                <td>{{ sensor.name }}</td>
                <td>Sensor</td>
                <td>{{ sensor.Data|floatformat:2 }}</td>
                <td>{{ sensor.unit }}</td>
                <td>{{ sensor.timestamp }}</td>
                <td>{{ sensor.details }}</td>
            </tr>
        {% endfor %}

        {% for actuator in actuators_table2 %}
            <tr>
                <td>{{ actuator.name }}</td>
                <td>Actuator</td>
                <td>{{ actuator.Data }}</td>
                <td></td> <!-- You might not have a unit for actuators, adjust as needed -->
                <td>{{ actuator.timestamp }}</td>
                <td></td> <!-- You might not have details for actuators, adjust as needed -->
            </tr>
        {% endfor %}
    </table>

    <!-- Third Table -->
    <h3>Table 3</h3>
    <table border="1">
        <!-- Table header for both sensors and actuators -->
        <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Data</th>
            <td>Unit</td>
            <th>Timestamp</th>
            <th>Details</th>
        </tr>
    
        <!-- Loop through sensors and actuators and display data for Table 3 -->
        {% for sensor in sensors_table3 %}
            <tr>
                <td>{{ sensor.name }}</td>
                <td>Sensor</td>
                <td>{{ sensor.Data|floatformat:2 }}</td>
                <td>{{ sensor.unit }}</td>
                <td>{{ sensor.timestamp }}</td>
                <td>{{ sensor.details }}</td>
            </tr>
        {% endfor %}

        {% for actuator in actuators_table3 %}
            <tr>
                <td>{{ actuator.name }}</td>
                <td>Actuator</td>
                <td>{{ actuator.Data }}</td>
                <td></td> <!-- You might not have a unit for actuators, adjust as needed -->
                <td>{{ actuator.timestamp }}</td>
                <td></td> <!-- You might not have details for actuators, adjust as needed -->
            </tr>
        {% endfor %}
    </table>

    <!-- Your JavaScript code for auto-refresh -->
    <script>
        function autoRefresh() {
            setTimeout(function () {
                location.reload();
            }, 1000);
        }

        autoRefresh();
    </script>
</body>
</html>

#######

# SensorApp/views.py

from django.shortcuts import render
from SmartHospitalSystem.models import Sensor_List_int
from SmartHospitalSystem.models import Actuator_List
from datetime import datetime
import paho.mqtt.client as mqtt

# List of sensor names (assuming they are the same as the sensor topics)
sensor_names = ["water_level_sensor", "heart_beat_sensor", "flourescent_based_sensor",
                "camera_sensor", "UV-C_sensor", "thermal_sensor", "room_pressure_sensor",
                "temperature_sensor", "humidity_sensor"]

# Global dictionary to store the latest sensor data for each sensor
latest_sensor_data_dict = {}

# Global list to store the last 100 sensor readings
sensor_data_history_list = []

def on_connect(client, userdata, flags, rc, ):
    print("Connected with result code " + str(rc))

    # Subscribe to topics for all sensors
    for sensor_name in sensor_names:
        client.subscribe(sensor_name)

def on_message(client, userdata, msg):
    global sensor_data_history_list

    sensor_name = msg.topic
    latest_sensor_data = float(msg.payload.decode())

    # Add the latest sensor data to the history list
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sensor_data_history_list.append({'sensor_name': sensor_name, 'data': latest_sensor_data, 'timestamp': current_time})

    # Keep only the last 100 sensor readings in the list
    sensor_data_history_list = sensor_data_history_list[-100:]

    # Update the latest sensor data in the dictionary
    latest_sensor_data_dict[sensor_name] = latest_sensor_data


# Set up the MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_broker_address = "127.0.0.1"
mqtt_client.connect(mqtt_broker_address, 1889)
mqtt_client.loop_start()

def update_page(request):
    global sensor_data_history_list

    # Update Sensor_List_int objects
    for sensor_name in sensor_names:
        if sensor_name in latest_sensor_data_dict:
            latest_sensor_data = latest_sensor_data_dict[sensor_name]

            sensor = Sensor_List_int.objects.get(name=sensor_name)
            sensor.Data = latest_sensor_data
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sensor.timestamp = current_time
            sensor.save()

    # Update Actuator_List objects
    actuators = Actuator_List.objects.all().filter(sensor_name__in=sensor_names)

    for actuator in actuators:
        associated_sensor = Sensor_List_int.objects.get(name=actuator.sensor_name)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        actuator.timestamp = current_time

        if actuator.activation_condition and isinstance(actuator.activation_condition, dict):
            sensor_value = int(associated_sensor.Data)

            if str(sensor_value) in actuator.activation_condition:
                actuator.Data = actuator.activation_condition[str(sensor_value)]
            else:
                actuator.Data = "Closed"
        else:
            if associated_sensor.Data >= actuator.threshold:
                if actuator.turn_on_when_exceeded:
                    actuator.Data = "on"
                else:
                    actuator.Data = "off"
            else:
                if actuator.turn_on_when_exceeded:
                    actuator.Data = "off"
                else:
                    actuator.Data = "on"

        actuator.save()

    # Retrieve Sensor_List_int and Actuator_List objects for rendering
    sensors = Sensor_List_int.objects.all()

    # Divide the sensors and actuators into three equal parts
    num_sensors = len(sensors)
    num_actuators = len(actuators)

    sensors_per_table = num_sensors // 3
    actuators_per_table = num_actuators // 3

    sensors_table1 = sensors[:sensors_per_table]
    sensors_table2 = sensors[sensors_per_table:2 * sensors_per_table]
    sensors_table3 = sensors[2 * sensors_per_table:]

    actuators_table1 = actuators[:actuators_per_table]
    actuators_table2 = actuators[actuators_per_table:2 * actuators_per_table]
    actuators_table3 = actuators[2 * actuators_per_table:]

    last_100_sensor_data = [entry['data'] for entry in sensor_data_history_list]

    return render(request, 'SmartHospitalSystem/base.html', {'sensors_table1': sensors_table1, 'sensors_table2': sensors_table2, 'sensors_table3': sensors_table3, 'actuators_table1': actuators_table1, 'actuators_table2': actuators_table2, 'actuators_table3': actuators_table3, 'last_100_sensor_data': last_100_sensor_data})
