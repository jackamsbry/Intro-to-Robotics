#!/usr/bin/env pybricks-micropython

from pybricks import ev3brick as brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import (Port, Stop, Direction, Button, Color,
                                 SoundFile, ImageFile, Align)
from pybricks.tools import print, wait, StopWatch
from pybricks.robotics import DriveBase
from passwords import Key

import ubinascii, ujson, utime, urequests
from pybricks.ev3devio import Ev3devSensor 
import ev3dev2
from ev3dev2.port import LegoPort 

# Write your program here

def main():
     left = Motor(Port.A)
     right = Motor(Port.D)
     light = ColorSensor(Port.S1)
     robot = DriveBase(left, right, 56, 152)
     uartPort = LegoPort('ev3-ports:in1')

     while True:
          reflection = light.reflection()
     
          if reflection < 70:
               Put_SL('line','BOOLEAN','true')
          else: 
               Put_SL('line','BOOLEAN','false')

          #robot.drive(0,10)

