#!/usr/bin/env pybricks-micropython

from pybricks import ev3brick as brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import (Port, Stop, Direction, Button, Color,
                                 SoundFile, ImageFile, Align)
from pybricks.tools import print, wait, StopWatch
from pybricks.robotics import DriveBase
from math import *

import utime
from pybricks.iodevices import UARTDevice



def moveEncode(x, y):
    x = int(x)
    y = int(y)

    moveCMD = (x<<4) | (y>>4)
    moveCMD = bytes(moveCMD)
    return moveCMD

def constrain(number, range):
    if number > range[1]:
        print(number)
        number = range[1]
    elif number < range[0]:
        print(number)
        number = range[0]
    return number

#Main Function
def main():
    joyMove = TouchSensor(Port.S1)
    xMotor = Motor(Port.A)
    yMotor = Motor(Port.D)
    resetAngle = TouchSensor(Port.S3)
    uartComm = UARTDevice(Port.S2, 9600)

    while True:
        #initial angle reading (correcting signs of angles)
        x = - xMotor.angle()
        y = - yMotor.angle()
        x += 90
        y += 90
        #convert x and y values to a number between 0 and 127
        x *= (128/180)
        y *= (128/180)
        #constrain numbers to be within range of an 4 bit number
        x_scale = [0, 127]
        y_scale = [0, 127]
        x = constrain(x, x_scale)
        y = constrain(y, y_scale)
        #convert x and y to single 8 bit number
        moveCMD = moveEncode(x, y)

        if uartComm.waiting() > 0:
            uartComm.read()
        else:
            uartComm.write(moveCMD) 

        if resetAngle.pressed():
            xMotor.reset_angle(0)
            yMotor.reset_angle(0)

        if not joyMove.pressed():
            xMotor.stop(Stop.HOLD)
            yMotor.stop(Stop.HOLD)
        else:
            xMotor.stop(Stop.COAST)
            yMotor.stop(Stop.COAST)

main()
        




