#!/bin/python3
from subprocess import Popen, PIPE
import paho.mqtt.client as mqtt
import nmap
import time
import atexit
import os
import getopt
import sys

MQTT_PORT = 1883
MQTT_USERNAME = 'mqtt_client'
MQTT_PASSWORD = 'mqtt_client'

class MqttEngine:

    def __init__(self, name, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client = mqtt.Client("FING_ENGINE {}".format(name))
        self.client.username_pw_set(self.username, self.password)
        self.connect()

    def connect(self):
        self.client.connect(self.host, port = self.port, keepalive = 60, bind_address = "")

    def publish(self, device):
        ret = self.client.publish("fing/{}/ip_address".format(device.mac_address), device.ip_address, retain = True)
        ret = self.client.publish("fing/{}/last_update".format(device.mac_address), int(time.time()), retain = True)
        ret = self.client.publish("fing/{}/ap".format(device.mac_address), device.access_point, retain = True)
        if ret.rc != mqtt.MQTT_ERR_SUCCESS:
            print("MQTT error. Reconnect.")
            self.connect()

class Device:

    def __init__(self, ip_address, mac_address, status, access_point):
        self.ip_address = ip_address
        self.mac_address = mac_address
        self.status = status
        self.access_point = access_point

    def __str__(self):
        return "<{},{}:{}>".format(
            self.ip_address,
            self.mac_address,
            self.status
        )

class FingEngine:

    def __init__(self, subnet, access_point):
        self.subnet = subnet
        self.access_point = access_point
        self.process = None
        atexit.register(self.on_exit)

    def run(self):
        fing_cmd = "fing -n {} -r 1 -o table,csv --silent".format(self.subnet)
        self.process = Popen("exec " + fing_cmd, stdout=PIPE, shell=True, preexec_fn=os.setsid)
        poll = self.process.poll()
        while poll is None:
            line = self.process.stdout.readline().rstrip()
            if line:
                input = line.decode().split(";")
                yield Device(input[0], input[5], input[2], self.access_point)
            poll = self.process.poll()

    def on_exit(self):
        self.process.kill()

class NmapEngine:

    def __init__(self, subnet, access_point):
        self.subnet = subnet
        self.access_point = access_point
        self.process = None
        self.nm = nmap.PortScanner()

    def run(self):
        r = self.nm.scan(hosts=self.subnet, arguments='-sn')
        for host in self.nm.all_hosts():
            if "mac" in self.nm[host]["addresses"]:
                yield Device(host, self.nm[host]["addresses"]["mac"], None, self.access_point)

def main(argv):
    param_AP = None
    param_SUBNET = None
    param_MQTTBROKER = None

    try:
        opts, args = getopt.getopt(argv,"hn:a:m:",["subnet=","apname="])
    except getopt.GetoptError:
        print('main.py -n SUBNET -a AP_NAME -m MQTT_BROKER')
        print('main.py -n 192.168.0.0/24 -a TELENET -m 192.168.0.173')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('main.py -n SUBNET -a AP_NAME -m MQTT_BROKER')
            print('main.py -n 192.168.0.0/24 -a TELENET -m 192.168.0.173')
            sys.exit()
        elif opt in ("-n", "--subnet"):
            param_SUBNET = arg
        elif opt in ("-a", "--apname"):
            param_AP = arg
        elif opt in ("-m"):
            param_MQTTBROKER = arg

    if(param_SUBNET is None or param_AP is None or param_MQTTBROKER is None):
        print("A param is NONE")
        sys.exit()

    nmap = NmapEngine(param_SUBNET, param_AP)
    mqtt_client = MqttEngine(param_AP, param_MQTTBROKER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD)
    while True:
        try:
            for device_info in nmap.run():
                # print(device_info)
                mqtt_client.publish(device_info)
        except TypeError:
            pass


if __name__ == "__main__":
    main(sys.argv[1:])
