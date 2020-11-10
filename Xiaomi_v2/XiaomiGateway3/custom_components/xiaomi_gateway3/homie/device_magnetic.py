#!/usr/bin/env python

from homie.device_state import Device_State
from homie.node.node_state import Node_State
from homie.node.node_integer import Node_Integer
from homie.node.property.property_battery import Property_Battery

import logging

logger = logging.getLogger(__name__)


class Device_Magnetic(Device_State):

    def __init__(self, device_id=None, name=None, homie_settings=None, mqtt_settings=None,state_values=None):

        super().__init__ (device_id, name, homie_settings, mqtt_settings, state_values)

        self.add_node(Node_State(self,id='state',name='State',state_values=state_values,set_state=self.set_state))

        self.add_node(Node_Integer(self, id="battery", set_value=self.set_value))
        self.battery = Property_Battery(self.get_node("battery"))
        self.get_node("battery").add_property(self.battery)

        self.start()

    def update_battery(self,battery):
        logger.info ('Updated Battery {}'.format(battery))
        self.battery.value = battery
        self.get_node("battery").publish_properties(qos=0)

    def set_value(self,value):#received commands from clients
        # subclass must override and provide logic to set the device
        logger.debug ('Integer Set {}'.format(value))