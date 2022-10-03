#!/bin/python3
from subprocess import Popen, PIPE
import paho.mqtt.client as mqtt
import time
import atexit
import os
import getopt
import sys

MQTT_PORT = 1883
MQTT_USERNAME = 'mqtt_client'
MQTT_PASSWORD = 'mqtt_client'

class MqttEngine:

    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.cb = None
        self.client = mqtt.Client("VERIFY_ONLINE_ENGINE")
        self.client.username_pw_set(self.username, self.password)
        self.client.on_message = self.on_message
        self.client.connect(self.host, port = self.port, keepalive = 60, bind_address = "")
        self.client.loop_start()

    def publish(self, topic, value):
        self.client.publish(topic, value, retain = True)

    def subscribe(self, topic):
        # print("Subscribe to topic {}".format(topic))
        self.client.subscribe(topic, 0)

    def unsubscribe(self, topic):
        # print("Unsubscribe from topic {}".format(topic))
        self.client.unsubscribe(topic, 0)

    def on_message(self, client, userdata, message):
        if self.cb is not None:
            self.cb(
                message.topic,
                str(message.payload.decode("utf-8"))
            )

    def set_callback(self, cb):
        self.cb = cb

def main(argv):
    param_MQTTBROKER = None
    param_TIMEDIFF = 0

    try:
        opts, args = getopt.getopt(argv,"hm:t:",[])
    except getopt.GetoptError:
        print('main.py -m MQTT_BROKER -t TIMEDIFF')
        print('main.py -m 192.168.0.173 -t 60')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('main.py -m MQTT_BROKER -t TIMEDIFF')
            print('main.py -m 192.168.0.173 -t 60')
            sys.exit()
        elif opt in ("-m"):
            param_MQTTBROKER = arg
        elif opt in ("-t"):
            param_TIMEDIFF = int(arg)

    if(param_MQTTBROKER is None or param_TIMEDIFF == 0):
        print('main.py -m MQTT_BROKER -t TIMEDIFF')
        print('main.py -m 192.168.0.173 -t 60')
        sys.exit()

    
    mqtt_client = MqttEngine(param_MQTTBROKER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD)

    def last_update(topic, value):
        last_update_time = int(value)
        epoch = int(time.time())
        is_online = 0
        if abs(last_update_time - epoch) < param_TIMEDIFF:
            is_online = 1
        online_topic = "{}/{}".format("/".join(topic.split("/")[:-1]), "online")
        mqtt_client.publish(online_topic, is_online)

    mqtt_client.set_callback(last_update)
    while True:
        mqtt_client.subscribe("fing/+/last_update")
        time.sleep(10)
        mqtt_client.unsubscribe("fing/+/last_update")


if __name__ == "__main__":
    main(sys.argv[1:])
