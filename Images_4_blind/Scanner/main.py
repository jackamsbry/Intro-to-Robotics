#!/usr/bin/env pybricks-micropython

from pybricks import ev3brick as brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import (Port, Stop, Direction, Button, Color,
                                 SoundFile, ImageFile, Align)
from pybricks.tools import print, wait, StopWatch
from pybricks.robotics import DriveBase
from passwords import Key

from pybricks.iodevices import UARTDevice

# Write your program here

def main():
     left = Motor(Port.A)
     right = Motor(Port.D)
     light = ColorSensor(Port.S1)
     robot = DriveBase(left, right, 56, 152)
     uartComm = UARTDevice(Port.S2, 9600)

     while True:
          reflection = light.reflection()
     
          if uartComm.waiting() > 0:
               data = uartComm.read()
               data = str(data)
               print(data)
               x = int(data[:-4])
               y = int(data[-4:])


          if reflection > 70:
               t = bytes(True)
               uartComm.write(t)
          
          speed = y - 64
          direction = x -64
          robot.drive(speed, direction)

main()