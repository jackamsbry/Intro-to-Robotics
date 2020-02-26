#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
from pybricks.iodevices import UARTDevice

# Write your program here
ev3 = EV3Brick()
ev3.speaker.beep()

hopperMotor = Motor(Port.D)
conveyorMotor = Motor(Port.A)
bucketMotor = Motor(Port.B)
light = ColorSensor(Port.S1)

uart = UARTDevice(Port.S4, 115200, timeout=0)
time = StopWatch()
#Set up a queue for bricks on the conveyor belt
brickQueue = []

count = 0
reflectMean = 0
reflectMeanNum = 0
wasBrick = 0
meanSize = 10
numStep = 0
redPos = 0
trashPos = 180 
currPos = 0

bucketMotor.reset_angle(0)
time.reset()
time.resume()


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
        if reflectMean > 0.5:
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
        getData = uart.read(1).decode('utf-8')
        print(getData)
        isRed = True if getData == "b'0'" else False

    except Exception as errMsg:
        #print("Read Failed")
        print(errMsg)

    try:
        if (time.time() > (brickQueue[0] + 10000)):
            brickQueue.pop(0)
            if isRed == True:
                if currPos == 180:
                    bucketMotor.run_target(50, redPos)
                    currPos = redPos
                else:
                    pass
            else:
                if currPos == 0:
                    bucketMotor.run_target(50, trashPos)
                    currPos = trashPos
                else:
                    pass
    except:
        print('Nothing in Queue')

    count += 1