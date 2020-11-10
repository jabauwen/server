import logging
import threading
import time
from utils import *
from gateway3 import *
from homie.device_temperature_humidity_battery import *
from homie.device_magnetic import *
from homie.device_state import *
from homie.node.node_base import *

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

# Class for generic Xiaomi object:
class Xiaomi_Object:

    def __init__(self, mqtt_settings, device_id, name):
        self.mqtt_settings = mqtt_settings
        self.device_id = device_id
        self.name = name


# Class for door information:
class Xiaomi_Door(Xiaomi_Object):

    DEBOUNCE_TIMEOUT = 2

    def __init__(self,  mqtt_settings, device_id, name, state_values = "closed,open"):
        super().__init__(mqtt_settings, device_id, name)
        self.state_values = state_values
        self.xiaomi_object = Device_Magnetic(
            mqtt_settings = self.mqtt_settings,
            device_id = self.device_id,
            name = self.name,
            state_values = self.state_values)
        self.last_alarm_timestamp = 0
    
    def update_door(self, source, values):
        print("Update door for {} : {}".format(source, values))
        if "battery" in values:
            print("Battery {}".format(values["battery"]))
            self.xiaomi_object.update_battery(values["battery"])
        if "contact" in values:
            print("Update contact")
            if values["contact"] == 1:
                self.xiaomi_object.update_state("open")
            else:
                if time.time() - self.last_alarm_timestamp > self.DEBOUNCE_TIMEOUT:
                    self.xiaomi_object.update_state("closed")
                    self.last_alarm_timestamp = time.time()

# Class for weather information:
class Xiaomi_Weather(Xiaomi_Object):

    def __init__(self,  mqtt_settings, device_id, name, temp_units = "C"):
        super().__init__(mqtt_settings, device_id, name)
        self.temp_units = temp_units
        self.xiaomi_object = Device_Temperature_Humidity_Battery(
            mqtt_settings = self.mqtt_settings,
            device_id = self.device_id,
            name = self.name,
            temp_units = self.temp_units)
        self.xiaomi_object.register_status_properties(
            Node_Base(
                self.xiaomi_object,
                'status',
                'Status',
                'status'
            )
        )

    def update_weather(self, source, values):
        print("Update weather for {} : {}".format(source, values))

        if "temperature" in values:
            print("Temperature {}".format(values["temperature"]))
            self.xiaomi_object.update_temperature(values["temperature"])
        
        if "humidity" in values:
            print("Humidity {}".format(values["humidity"]))
            self.xiaomi_object.update_humidity(values["humidity"])

        if "pressure" in values:
            print("Pressure {}".format(values["pressure"]))
        
        if "battery" in values:
            print("Battery {}".format(values["battery"]))
            self.xiaomi_object.update_battery(values["battery"])
        
        self.xiaomi_object.node.publish_properties(qos=0)


# Class for handling all xiaomi gateway functionality
class Xiaomi_Gateway:

    def __init__(self, xiaomi_ip, xiaomi_token, mqtt_settings):
        self.mqtt_settings = mqtt_settings
        self.connected_devices = {}
        self.xiaomi_gateway = Gateway3(xiaomi_ip, xiaomi_token)
        self.xiaomi_gateway.deploy()

    def register_devices(self):
        for device in self.xiaomi_gateway.devices:
            if device["model"] == "lumi.weather.v1":
                self.connected_devices["{}.weather".format(device["did"])] = Xiaomi_Weather(
                    mqtt_settings = self.mqtt_settings,
                    device_id="{}.weather".format(device["did"]).replace(".",""),
                    name="{}.weather".format(device["did"]))
                self.xiaomi_gateway.add_update(device["did"], self.connected_devices["{}.weather".format(device["did"])].update_weather)
                self.connected_devices["{}.weather".format(device["did"])].update_weather(device["did"], device["init"])
            elif device["model"] == "lumi.sensor_magnet.v2":
                self.connected_devices["{}.door".format(device["did"])] = Xiaomi_Door(
                    mqtt_settings = self.mqtt_settings,
                    device_id="{}.door".format(device["did"]).replace(".",""),
                    name="{}.door".format(device["did"]))
                
                self.xiaomi_gateway.add_update(device["did"], self.connected_devices["{}.door".format(device["did"])].update_door)
                self.connected_devices["{}.door".format(device["did"])].update_door(device["did"], device["init"])

    def run(self):
        self.xiaomi_gateway.run()


# MAIN:
xiaomi_ip="192.168.0.171"
xiaomi_token="73734c49554d42764d415175786b7a48"
mqtt_settings = {
    'MQTT_BROKER' : '192.168.0.173',
    'MQTT_PORT' : 1883,
}

gateway_controller = Xiaomi_Gateway(xiaomi_ip, xiaomi_token, mqtt_settings)
gateway_controller.register_devices()
gateway_controller.run()

while True:
    time.sleep(10)
