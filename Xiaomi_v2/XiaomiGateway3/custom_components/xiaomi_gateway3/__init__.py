import logging

from utils import *
from gateway3 import *

_LOGGER = logging.getLogger(__name__)

def update_weather(values):
    print("Weather update {}".format(values))

def update_door(values):
    print("Door update {}".format(values))

xiaomi_gateway = Gateway3("192.168.0.171", "754d4b413147516c4a47515158426d64")
xiaomi_gateway.deploy()
for device in xiaomi_gateway.devices:
    if device["model"] == "lumi.weather.v1":
        xiaomi_gateway.add_update(device["did"], update_weather)
    elif device["model"] == "lumi.sensor_magnet.v2":
        xiaomi_gateway.add_update(device["did"], update_door)

xiaomi_gateway.run()