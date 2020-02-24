#!/usr/bin/env pybricks-micropython

from pybricks.parameters import Port
from pybricks.ev3devio import Ev3devSensor

class EV3Sensor(Ev3devSensor):
    _ev3dev_driver_name='ev3-analog-01'
    def read(self):
        self._mode('ANALOG')
        return self._value(0)
