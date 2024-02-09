# SensorApp/views.py

from django.shortcuts import render
from SmartHospitalSystem.models import Sensor_List_int
from SmartHospitalSystem.models import Actuator_List
from datetime import datetime
import paho.mqtt.client as mqtt
import pandas as pd
import numpy as np
from sklearn import linear_model
import joblib
import os
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from simple_history.models import HistoricalRecords
from itertools import chain
from itertools import groupby

# List of sensor names (assuming they are the same as the sensor topics)
sensor_names = ["IV_level_sensor", "heart_beat_sensor", "flourescent_based_sensor",
                "camera_sensor", "Microbial_sensor", "thermal_sensor", "room_pressure_sensor",
                "temperature_sensor", "humidity_sensor"]
actuator_names = ["Alert", "IV_flow_regulator", "Insulin_pump",
                "Laser_pointer", "Door_lock", "Disinfectant_spray", "Electric_damper", "HVAC_system", "Alarm"]
# Global dictionary to store the latest sensor data for each sensor
latest_sensor_data_dict = {}

# Global list to store the last 100 sensor readings
sensor_data_history_list = []
historical_sensor_data_dict = {sensor_name: [] for sensor_name in sensor_names}

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
    sensor_data_history_list = sensor_data_history_list[-20:]

    # Update the latest sensor data in the dictionary
    latest_sensor_data_dict[sensor_name] = latest_sensor_data
    historical_sensor_data_dict[sensor_name].append({'data': latest_sensor_data, 'timestamp': current_time})
    historical_sensor_data_dict[sensor_name] = historical_sensor_data_dict[sensor_name][-20:]

# Set up the MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_broker_address = "127.0.0.1"
mqtt_client.connect(mqtt_broker_address, 1889)
mqtt_client.loop_start()

def update_page(request):
    result_true_1_list = []
    result_true_2_list = []
    result_true_3_list = []
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
            
    # Retrieve Sensor_List_int and Actuator_List objects for rendering
    sensors = Sensor_List_int.objects.all()
    

    # Update Actuator_List objects
    actuators = Actuator_List.objects.all()

    # Divide the sensors and actuators into three equal parts
    num_sensors = len(sensors)
    num_actuators = len(actuators)

    sensors_per_table = num_sensors // 3
    actuators_per_table = num_actuators // 3  

    sensors_table1 = sensors[:sensors_per_table]
    sensors_table2 = sensors[sensors_per_table:2 * sensors_per_table]
    sensors_table3 = sensors[2 * sensors_per_table:]

    actuators_table1 =  actuators[:actuators_per_table]
    actuators_table2 = actuators[actuators_per_table:2 * actuators_per_table]
    actuators_table3 = actuators[2 * actuators_per_table:]

    for actuator in actuators_table1:

        file_name = str(actuator) + ".csv"
        script_dir = os.getcwd()
        csv_subdirectory = "csv"
        file_path = os.path.join(script_dir, csv_subdirectory, file_name)
        df = pd.read_csv(file_path)

        sensor_names_table1 = [sensor.name for sensor in sensors_table1]
        features = df[sensor_names_table1]
        target = df[str(actuator)]

        X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

        # Create a logistic regression model
        model = LogisticRegression()

        # Train the model
        model.fit(X_train, y_train)

        # Make predictions on the test set
        predictions = model.predict(X_test)

        # Calculate accuracy (you might want to store or log this value for evaluation)
        accuracy = accuracy_score(y_test, predictions)

        # Use the latest sensor data for prediction
        #new_data = [[latest_sensor_data_dict[sensor] for sensor in features.columns]]
 

        new_data = pd.DataFrame( 
        np.array([[latest_sensor_data_dict[sensor] for sensor in features.columns]]).reshape(1, -1), 
        columns=['IV_level_sensor', 'heart_beat_sensor', 'flourescent_based_sensor'] 
    )
        result = model.predict(new_data)

        actuator.Data = result[0]
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        actuator.timestamp = current_time
        actuator.save()
        
        result_true_1_list.append(result[0])
        #print(f'{actuator} : {new_data} results in {result} with an accuracy of {accuracy}')

    for actuator in actuators_table2:

        file_name = str(actuator) + ".csv"
        script_dir = os.getcwd()
        csv_subdirectory = "csv"
        file_path = os.path.join(script_dir, csv_subdirectory, file_name)
        df = pd.read_csv(file_path)

        sensor_names_table2 = [sensor.name for sensor in sensors_table2]
        features = df[sensor_names_table2]
        target = df[str(actuator)]

        X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

        # Create a logistic regression model
        model = LogisticRegression()

        # Train the model
        model.fit(X_train, y_train)

        # Make predictions on the test set
        predictions = model.predict(X_test)

        # Calculate accuracy (you might want to store or log this value for evaluation)
        accuracy = accuracy_score(y_test, predictions)

        # Use the latest sensor data for prediction
        new_data = pd.DataFrame( 
        np.array([[latest_sensor_data_dict[sensor] for sensor in features.columns]]).reshape(1, -1), 
        columns=['camera_sensor', 'Microbial_sensor', 'thermal_sensor'] 
    )
        result = model.predict(new_data)


        actuator.Data = result[0]

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        actuator.timestamp = current_time
        actuator.save()
        
        result_true_2_list.append(result[0])


    for actuator in actuators_table3:
        
        file_name = str(actuator) + ".csv"
        script_dir = os.getcwd()
        csv_subdirectory = "csv"
        file_path = os.path.join(script_dir, csv_subdirectory, file_name)
        df = pd.read_csv(file_path)

        sensor_names_table3 = [sensor.name for sensor in sensors_table3]
        features = df[sensor_names_table3]
        target = df[str(actuator)]

        X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
        
        # Create a logistic regression model
        model = LogisticRegression()

        # Train the model
        model.fit(X_train, y_train)

        # Make predictions on the test set
        predictions = model.predict(X_test)

        # Calculate accuracy (you might want to store or log this value for evaluation)
        accuracy = accuracy_score(y_test, predictions)

        # Use the latest sensor data for prediction
        new_data = pd.DataFrame( 
            np.array([[latest_sensor_data_dict[sensor] for sensor in features.columns]]).reshape(1, -1), 
            columns=['room_pressure_sensor','temperature_sensor','humidity_sensor'] )

        result = model.predict(new_data)
        actuator.Data = result[0]

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        actuator.timestamp = current_time
        actuator.save()
        
        result_true_3_list.append(result[0])
 


    last_20_sensor_data_per_sensor = {sensor_name: [entry['data'] for entry in historical_sensor_data_dict[sensor_name]] for sensor_name in sensor_names}

    return render(request, 'SmartHospitalSystem/base.html', {
        'sensors_table1': sensors_table1,
        'sensors_table2': sensors_table2,
        'sensors_table3': sensors_table3,
        'actuators_table1': actuators_table1,
        'actuators_table2': actuators_table2,
        'actuators_table3': actuators_table3,
        'last_100_sensor_data': last_20_sensor_data_per_sensor,
        'result_true_1_list': result_true_1_list,
        'result_true_2_list': result_true_2_list,
        'result_true_3_list': result_true_3_list,
    })

class InfoPageView(View):
    def get(self, request, *args, **kwargs):
        # You can add any additional logic here if needed
        return render(request, 'SmartHospitalSystem/info.html')

class Log1PageView(View):
    template_name = 'SmartHospitalSystem/log1.html'
    paginate_by = 120

    def get(self, request, *args, **kwargs):
        sensors_of_interest = ["IV_level_sensor", "heart_beat_sensor", "flourescent_based_sensor"]
        sensor_entries = Sensor_List_int.history.filter(name__in=sensors_of_interest).order_by('-timestamp')

        # Retrieve historical entries for specific actuators
        actuator_of_interest = ["Alert", "IV_flow_regulator", "Insulin_pump"]
        actuator_entries = Actuator_List.history.filter(name__in=actuator_of_interest).order_by('-timestamp')

        # Combine sensor entries for both IV Level and Heartbeat Sensors
        combined_entries = list(chain(sensor_entries, actuator_entries))

        # Sort the combined entries by timestamp
        combined_entries.sort(key=lambda entry: entry.timestamp, reverse=True)
 
        # Pagination for combined entries
        paginator = Paginator(combined_entries, self.paginate_by)
        page = request.GET.get('page')

        try:
            log_entries = paginator.page(page)
        except PageNotAnInteger:
            log_entries = paginator.page(1)
        except EmptyPage:
            log_entries = paginator.page(paginator.num_pages)

        return render(
            request,
            self.template_name,
            {
                'log_entries': log_entries,
            }
        )
    
class Log2PageView(View):
    template_name = 'SmartHospitalSystem/log2.html'
    paginate_by = 120

    def get(self, request, *args, **kwargs):
        sensors_of_interest = ["camera_sensor", "Microbial_sensor", "thermal_sensor"]
        sensor_entries = Sensor_List_int.history.filter(name__in=sensors_of_interest).order_by('-timestamp')

        # Retrieve historical entries for specific actuators
        actuator_of_interest = ["Laser_pointer", "Door_lock", "Disinfectant_spray"]
        actuator_entries = Actuator_List.history.filter(name__in=actuator_of_interest).order_by('-timestamp')

        # Combine sensor entries for both IV Level and Heartbeat Sensors
        combined_entries = list(chain(sensor_entries, actuator_entries))

        # Sort the combined entries by timestamp
        combined_entries.sort(key=lambda entry: entry.timestamp, reverse=True)
 
        # Pagination for combined entries
        paginator = Paginator(combined_entries, self.paginate_by)
        page = request.GET.get('page')

        try:
            log_entries = paginator.page(page)
        except PageNotAnInteger:
            log_entries = paginator.page(1)
        except EmptyPage:
            log_entries = paginator.page(paginator.num_pages)

        return render(
            request,
            self.template_name,
            {
                'log_entries': log_entries,
            }
        )
    
class Log3PageView(View):
    template_name = 'SmartHospitalSystem/log3.html'
    paginate_by = 120

    def get(self, request, *args, **kwargs):
        sensors_of_interest = ["room_pressure_sensor","temperature_sensor", "humidity_sensor"]
        sensor_entries = Sensor_List_int.history.filter(name__in=sensors_of_interest).order_by('-timestamp')

        # Retrieve historical entries for specific actuators
        actuator_of_interest = ["Electric_damper", "HVAC_system", "Alarm"]
        actuator_entries = Actuator_List.history.filter(name__in=actuator_of_interest).order_by('-timestamp')

        # Combine sensor entries for both IV Level and Heartbeat Sensors
        combined_entries = list(chain(sensor_entries, actuator_entries))

        # Sort the combined entries by timestamp
        combined_entries.sort(key=lambda entry: entry.timestamp, reverse=True)
 
        # Pagination for combined entries
        paginator = Paginator(combined_entries, self.paginate_by)
        page = request.GET.get('page')

        try:
            log_entries = paginator.page(page)
        except PageNotAnInteger:
            log_entries = paginator.page(1)
        except EmptyPage:
            log_entries = paginator.page(paginator.num_pages)

        return render(
            request,
            self.template_name,
            {
                'log_entries': log_entries,
            }
        )