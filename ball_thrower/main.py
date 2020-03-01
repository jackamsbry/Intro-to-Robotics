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
launchMotor = Motor(Port.A, Direction.CLOCKWISE, [40, 24])

distanceSensor = UltrasonicSensor(Port.S4)

#Define Constants
ballOffsetx = -66/1000
ballOffsety = 140/1000
armRadius = 144/1000
cupHeight = 122/1000
cupRadius = 100/2000
armMass = 24
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
    dx = dist - ballOffsetx + cupRadius
    dy = cupHeight - (ballOffsety + (.02529 * math.sin(angle_rad)))
    speed = (3*math.sqrt(109/2)*dx*(1/math.cos(angle_rad)))/(10*math.sqrt(dx*math.tan(angle_rad)-dy))
    return speed
    

def momentumCalc(speed):
    mA = armMass
    mB = ballMass
    massRatio = mB/mA
    epsilon = 0.75
    vB2 = speed
    vA1 = (vB2 * (massRatio + 1))/(1 + epsilon)
    return (vA1)/armRadius

def bestArc(dist):
    return 0

def main():
    releaseAngle = 0
    #Bring arm up before it hits the ball
    launchMotor.run_angle(200, -120)
    wasLaunch = False

    while True:
        sum = 0
        launchMotor.stop(Stop.HOLD)
        #Find the average distance from several data points
        for value in range(10):
            dist = distanceSensor.distance()/1000
            sum += dist
        averageDist = sum/10
        isLaunch = True if Get_SL("isLaunch") == "true" else False
        findAngle = True if Get_SL("findAngle") == "true" else False
        if findAngle:
            releaseAngle = bestArc(averageDist)
        else:
            releaseAngle = int(Get_SL("releaseAngle"))
        angleMotor.run_target(100, releaseAngle)
        speed = newtonSpeed(averageDist, releaseAngle)
        ang_speed = momentumCalc(speed)
        ang_speed = round(math.degrees(ang_speed))
        print(ang_speed)

        if isLaunch == True and wasLaunch == False:
            launchMotor.run_angle(ang_speed, 270)
            launchMotor.stop(Stop.HOLD)
            wasLaunch = True

        if isLaunch == False and wasLaunch == True:
            launchMotor.run_angle(500, -270)
            launchMotor.stop(Stop.HOLD)
            wasLaunch = False

main()
