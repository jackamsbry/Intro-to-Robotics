#!/usr/bin/env pybricks-micropython

from pybricks import ev3brick as brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import (Port, Stop, Direction, Button, Color,
                                 SoundFile, ImageFile, Align)
from pybricks.tools import print, wait, StopWatch
from pybricks.robotics import DriveBase

from pybricks.ev3devio import Ev3devSensor 
import utime
import uio
import ev3dev2
from ev3Sensor import EV3Sensor
from ev3dev2.port import LegoPort

# Write your program here


left = Motor(Port.D)
right = Motor(Port.A)

ultrasonic = UltrasonicSensor(Port.S2)

dist_thresh = 100

filename = './log.txt'
f 

def main():
    brick.sound.beep()
    sens = LegoPort(address ='ev3-ports:in1') # which port?? 1,2,3, or 4
    sens.mode = 'ev3-analog'
    # sens2 = LegoPort(address ='ev3-ports:in4')
    # sens2.mode = 'ev3-analog'
    utime.sleep(0.5)
    sensor_left = EV3Sensor(Port.S1) # same port as above
    while True:
        print(sensor_left.read())
        wait(200)

main()