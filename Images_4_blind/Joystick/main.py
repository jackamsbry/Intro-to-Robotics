#!/usr/bin/env pybricks-micropython

from pybricks import ev3brick as brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import (Port, Stop, Direction, Button, Color,
                                 SoundFile, ImageFile, Align)
from pybricks.tools import print, wait, StopWatch
from pybricks.robotics import DriveBase
from math import *

import utime, ujson
from pybricks.iodevices import UARTDevice



def moveEncode(x, y):
    coords = {'x':x, 'y':y}
    moveCMD =  ujson.dumps(coords)
    wait(100)
    return moveCMD + ''.join(['B' for i in range(32-len(moveCMD))])

#Main Function
def main():
    joyMove = TouchSensor(Port.S1)
    xMotor = Motor(Port.A)
    yMotor = Motor(Port.D)
    resetAngle = TouchSensor(Port.S3)
    uartComm = UARTDevice(Port.S2, 9600)
    #main loop
    while True:
        #initial angle reading (correcting signs of angles)
        x = - xMotor.angle()
        y = - yMotor.angle()
        
        #Encode the values in a json object
        moveCMD = moveEncode(x, y)

        #try to read values from serial
        try:
            data_raw = uartComm.read(32)
            data = ujson.loads(data_raw)
            isLine = data['isLine']

        except Exception as e:
            uartComm.clear()
            print(e)
            print("Buffer Cleared")
        
        #try to write values to serial    
        try:
            uartComm.write(moveCMD) 
        except Exception as e:
            print(e)
            print("Write Failed")

        if resetAngle.pressed():
            xMotor.reset_angle(0)
            yMotor.reset_angle(0)
        if isLine:
            xMotor.run(0.4 * x)
            yMotor.run(0.4 * y)
        else: 
            xMotor.stop(Stop.COAST)
            yMotor.stop(Stop.COAST)

main()
        




