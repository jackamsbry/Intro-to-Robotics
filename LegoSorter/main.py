#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
from pybricks.iodevices import UARTDevice
import serial

# Write your program here
ev3 = EV3Brick()
ev3.speaker.beep()

hopperMotor = Motor(Port.D)
conveyorMotor = Motor(Port.A)
light = ColorSensor(Port.S1)

uart = UARTDevice(Port.S4, 115200, timeout=0)

count = 0
reflectMean = 0
reflectMeanNum = 0
meanSize = 10
numStep = 0

while True:
    hopperMotor.dc(60)
    conveyorMotor.run(-35)
    reflect = light.reflection()
    if count % meanSize:
        reflectMeanNum += reflect
    else: 
        reflectMean = reflectMeanNum / meanSize
        print(reflectMean)
        if reflectMean > 0 :
            print("Brick Detected")
            isBrick = bytes('1', 'utf-8')
            uart.write(isBrick)
            reflectMean = 0
            reflectMeanNum = 0
        else:
            print("No Brick")
            pass
    
    try:
        rawData = uart.read()
        
    except Exception as errMsg:
        print("Read Failed")
        print(errMsg)


    
    

    count += 1