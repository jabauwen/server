#!/usr/bin/env python

import sys
import time

import homie

from homie.support.helpers import validate_id
from homie.mqtt.homie_mqtt_client import connect_mqtt_client
from homie.support.repeating_timer import Repeating_Timer

import logging
logger = logging.getLogger(__name__)
logger.setLevel('INFO')

instance_count = 0 # used to track the number of device instances to allow for changing the default device id

repeating_timer = None # use common timer between all devices for updating state

DEVICE_STATES = [
    "init",
    "ready",
    "disconnected",
    "sleeping",
    "alert",
    "lost",
]

HOMIE_SETTINGS = {
    'version' : '3.0.1',
    'topic' : 'homie',
    'fw_name' : 'homie v3',
    'fw_version' : homie.__version__,
    'update_interval' : 60,
    'implementation' : sys.platform,
}


class Device_Base(object):

    def __init__(self, device_id=None, name=None, homie_settings={}, mqtt_settings={}):
        global instance_count
        instance_count = instance_count + 1
        self.instance_number = instance_count

        if device_id is None:
            device_id=self.generate_device_id()

        assert validate_id(device_id), 'Invalid device id {}'.format(device_id)
        self.device_id = device_id

        assert name
        self.name = name

        self._state = "init"

        self.homie_settings = self._homie_validate_settings (homie_settings)
        self.topic = "/".join((self.homie_settings ['topic'], self.device_id))

        #may need a way to set these
        self.retained = True
        self.qos = 1

        self.nodes = {}

        self.start_time = None

        self.nodes_published = False

        self.mqtt_client = connect_mqtt_client(self,mqtt_settings)

        self.mqtt_subscription_handlers = {}


    def generate_device_id(self):
        #logger.debug ('Device instances {}'.format(instance_count))
        #return "{:02x}".format(get_mac())+"{:04d}".format(instance_count)
        return "device{:04d}".format(self.instance_number)

    def start(self): # called after the device has been built with nodes and properties
        logger.debug ('Device startup')
        self.start_time = time.time()

        global repeating_timer
        if repeating_timer == None:
            repeating_timer = Repeating_Timer(self.homie_settings['update_interval'])

        repeating_timer.add_callback (self.publish_statistics)

        if self.mqtt_client.mqtt_connected: #run start up tasks if mqtt is ready, else wait for on_connect message from mqtt client
            self.mqtt_on_connection(True)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state, retain = True, qos = 1):
        if state in DEVICE_STATES:
            self._state = state
            self.publish( "/".join((self.topic, "$state")),self._state, retain, qos)
        else:
            logger.warning ('Homie Invalid device state {}'.format(state))

    def publish_attributes(self, retain=True, qos=0):
        mac,ip = self.mqtt_client.get_mac_ip_address()

        self.publish("/".join((self.topic, "$homie")),self.homie_settings ['version'], retain, qos)
        self.publish("/".join((self.topic, "$name")),self.name, retain, qos)
        self.publish("/".join((self.topic, "$localip")),ip, retain, qos)
        self.publish("/".join((self.topic, "$mac")),mac, retain, qos)
        self.publish("/".join((self.topic, "$fw/name")),self.homie_settings ['fw_name'], retain, qos)
        self.publish("/".join((self.topic, "$fw/version")),self.homie_settings ['fw_version'], retain, qos)
        self.publish("/".join((self.topic, "$implementation")),self.homie_settings ['implementation'], retain, qos)
        self.publish("/".join((self.topic, "$stats/interval")),self.homie_settings ['update_interval'], retain, qos)

        self.state = 'ready'

    def publish_statistics(self, retain=True, qos=1):
        self.publish("/".join((self.topic, "$stats/uptime")),time.time()-self.start_time, retain, qos)
        self.publish("/".join((self.topic, "$stats/interval")),self.homie_settings ['update_interval'], retain, qos)

    def add_subscription(self,topic,handler,qos=0): #subscription list to the required MQTT topics, used by properties to catch set topics
        self.mqtt_subscription_handlers [topic] = handler
        self.mqtt_client.subscribe (topic,qos)
        logger.debug ('MQTT subscribed to {}'.format(topic))

    def remove_subscription(self,topic):
        self.mqtt_client.unsubscribe (topic)
        del self.mqtt_subscription_handlers [topic]
        logger.debug ('MQTT unsubscribed to {}'.format(topic))

    def subscribe_topics(self):
        logger.debug('Device subscribing to topics')
        self.add_subscription ("/".join((self.topic, "$broadcast/#")),self.broadcast_handler) #get the broadcast events

        for _,node in self.nodes.items():
            for topic,handler in node.get_subscriptions().items():
                self.add_subscription(topic,handler)

    def add_node(self,node):
        self.nodes [node.id] = node

        if self.nodes_published: #update, publish property changes
            self.publish_nodes(self.retained, self.qos)

    def remove_node(self, node_id): # not tested, needs work removing topics
        del self.nodes [node_id]

        if self.nodes_published: #update, publish property changes
            self.publish_nodes(retain = False)

    def get_node(self,node_id):
        if node_id in self.nodes:
            return self.nodes [node_id]
        else:
            return None

    def publish_nodes(self, retain=True, qos=1):
        nodes = ",".join(self.nodes.keys())
        self.publish("/".join((self.topic, "$nodes")), nodes, retain, qos)

        self.nodes_published = True

        for _,node in self.nodes.items():
            node.publish_attributes(retain, qos)

    def broadcast_handler(self,topic,payload):#TBD
        logger.debug ('Device MQTT Homie Broadcast:  Topic {}, Payload {}'.format(topic,payload))

    def publish(self, topic, payload, retain=True, qos=1):
        logger.debug('Device MQTT publish topic: {}, retain {}, qos {}, payload: {}'.format(topic,retain,qos,payload))
        self.mqtt_client.publish(topic, payload, retain=retain, qos=qos)

    def _homie_validate_settings(self,settings):
        if settings is not None:
            for setting,value in HOMIE_SETTINGS.items():
                logger.debug('Homie settings {} {}'.format(setting,value))
                if not setting in settings:
                    settings [setting] = HOMIE_SETTINGS [setting]
        else:
            settings = HOMIE_SETTINGS

        return settings

    def mqtt_on_connection(self,connected):
        logger.debug("Device MQTT Connected state is {}".format(connected))

        if connected:
            self.publish_attributes()
            self.publish_nodes()
            self.subscribe_topics()

            if self.mqtt_client.using_shared_mqtt_client is False or self.instance_number == 1: # only set last will if NOT using shared client or if using shared client and this is the first device instance
                self.mqtt_client.set_will("/".join((self.topic, "$state")), "lost", retain=True, qos=1)
                logger.debug ('Device setting last will')

    def mqtt_on_message(self, topic, payload):
        if topic in self.mqtt_subscription_handlers:
            logger.debug ('Device MQTT Message: Topic {}, Payload {}'.format(topic,payload)) #for logging only, topic and handler for subsriptions above
            self.mqtt_subscription_handlers [topic] (topic, payload)
