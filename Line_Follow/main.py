#!/usr/bin/env pybricks-micropython

from pybricks import ev3brick as brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import (Port, Stop, Direction, Button, Color,
                                 SoundFile, ImageFile, Align)
from pybricks.tools import print, wait, StopWatch
from pybricks.robotics import DriveBase

import uio

# Write your program here
brick.sound.beep()

left = Motor(Port.D)
right = Motor(Port.A)

ultrasonic = UltrasonicSensor(Port.S1)

dist_thresh = 100

filename = './log.txt'
fin = uio.open(filename, )
while True:
    dist = ultrasonic.distance()
    kp = 0.8
    error = dist - dist_thresh
    
    speed = kp * error
    left.run(-speed)
    right.run(-speed)

