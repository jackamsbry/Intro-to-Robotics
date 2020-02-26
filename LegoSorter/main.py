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

from ucollections import deque


# Write your program here
ev3 = EV3Brick()
ev3.speaker.beep()

hopperMotor = Motor(Port.D)
conveyorMotor = Motor(Port.A)
bucketMotor = Motor(Port.B)
light = ColorSensor(Port.S1)

uart = UARTDevice(Port.S4, 115200, timeout=0)
time = Stopwatch()
#Set up a queue for bricks on the conveyor belt
brickQueue = deque((),maxlen=5)

count = 0
reflectMean = 0
reflectMeanNum = 0
wasBrick = 0
meanSize = 10
numStep = 0
redPos = 0
trashPos = 180 

bucketMotor.reset(0)
time.pause()
time.reset()


while True:
    hopperMotor.dc(60)
    conveyorMotor.run(-35)
    reflect = light.reflection()
    if count % meanSize:
        reflectMeanNum += reflect
    else: 
        reflectMean = reflectMeanNum / meanSize
        # Average every 10 readings
        reflectMean = reflectMeanNum / meanSize
        print(reflectMean)
        if reflectMean > 0.5 :
            print("Brick Detected")
            if wasBrick == 0:
                sendData = bytes('1', 'utf-8')
                uart.write(sendData)
                wasBrick = 1
                brickQueue.append(time.time())
            reflectMean = 0
            reflectMeanNum = 0
        else: 
            if wasBrick == 1:
                wasBrick = 0
            print("No Brick")

    # Try to read from serial port
    try:
        rawData = uart.read(1).decode('utf-8')
        isRed = True if rawData == '1' else False

    except Exception as errMsg:
        print("Read Failed")
        print(errMsg)


    try:
        if (time.time() > (brickQueue.popleft() + 10000):
            if isRed == True:
                bucketMotor.run_target(50, redPos)
            else:
                bucketMotor.run_target(50, trashPos)
        else:
            print('Wait for Brick to arrive')
    except:
        print('Nothing in Queue')

    count += 1