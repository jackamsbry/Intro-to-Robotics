#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
from passwords import Key as Key

import ubinascii, ujson, utime, urequests, math

# Write your program here
ev3 = EV3Brick()
ev3.speaker.beep()

angleMotor = Motor(Port.B, Direction.COUNTERCLOCKWISE)
launchMotor = Motor(Port.A, Direction.CLOCKWISE, [24, 40])

distanceSensor = UltrasonicSensor(Port.S4)

#Define Constants
ballOffsetx = -70/1000
ballOffsety = 140/1000
armRadius = 144/1000
cupHeight = 120/1000
armMass = 24 * 1.1
ballMass = 10

def SL_setup():
     urlBase = "https://api.systemlinkcloud.com/nitag/v2/tags/"
     headers = {"Accept":"application/json","x-ni-api-key":Key}
     return urlBase, headers
     
def Put_SL(Tag, Type, Value):
     urlBase, headers = SL_setup()
     urlValue = urlBase + Tag + "/values/current"
     propValue = {"value":{"type":Type,"value":Value}}
     try:
          reply = urequests.put(urlValue,headers=headers,json=propValue).text
     except Exception as e:
          print(e)         
          reply = 'failed'
     return reply

def Get_SL(Tag):
     urlBase, headers = SL_setup()
     urlValue = urlBase + Tag + "/values/current"
     try:
          value = urequests.get(urlValue,headers=headers).text
          data = ujson.loads(value)
          #print(data)
          result = data.get("value").get("value")
     except Exception as e:
          print(e)
          result = 'failed'
     return result
     
def Create_SL(Tag, Type):
     urlBase, headers = SL_setup()
     urlTag = urlBase + Tag
     propName={"type":Type,"path":Tag}
     try:
          urequests.put(urlTag,headers=headers,json=propName).text
     except Exception as e:
          print(e)

def newtonSpeed(dist, angle):
    angle_rad = math.radians(angle)
    dx = dist - ballOffsetx
    dy = cupHeight - ballOffsety
    speed = (3*math.sqrt(109/2)*dx*(1/math.cos(angle_rad)))/(10*math.sqrt(dx*math.tan(angle_rad)-dy))
    return speed
    

def momentumCalc(speed):
    mA = armMass
    mB = ballMass
    vA1 = speed
    vB1 = 0
    epsilon = 0.95
    vA2 = speed * epsilon
    vB2 = (mA/mB) * (vA1 - vA2) 
    return vB2/armRadius

def optimalArc(dist):
    return 0

def main():
    releaseAngle = 0
    wasLaunch = False

    while True:
        dist = distanceSensor.distance()/1000
        isLaunch = True if Get_SL("isLaunch") == "true" else False
        findAngle = True if Get_SL("findAngle") == "true" else False
        if findAngle:
            releaseAngle = optimalArc(dist)
        else:
            releaseAngle = int(Get_SL("releaseAngle"))
        angleMotor.run_target(100, releaseAngle)
        speed = newtonSpeed(dist, releaseAngle)
        ang_speed = momentumCalc(speed)
        ang_speed = round(math.degrees(ang_speed))

        if isLaunch == True and wasLaunch == False:
            launchMotor.run_angle(ang_speed, 270)
            launchMotor.stop(Stop.HOLD)
            wasLaunch = True

        if isLaunch == False and wasLaunch == True:
            launchMotor.run_angle(ang_speed, -270)
            launchMotor.stop(Stop.HOLD)
            wasLaunch = False

main()
