#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
from passwords import Key

# SYSTEMLINK STUFF
import ubinascii, ujson, urequests, utime

# Systemlink lego_shape key:
# 0 = NONE, 1 = ONExONE, 2 = ONExTHREE, 3 = TWOxTWO, 4 = TWOxTHREE, 5 = TWOxFOUR
    
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

# CONSTANTS
ev3 = EV3Brick()

# motors
claw = Motor(Port.A)
sort_motor = Motor(Port.B)

# angles
cam_angle = 0
oneXtwo = 45
oneXthree = 90
twoXtwo = 75
twoXthree = -45
twoXfour = -90
motor_open = 480
motor_close = 0

# speeds
claw_speed = 250
sort_speed = 50

# FUNCTIONS
# opens and closes brick holder
def drop():
    claw.run_target(claw_speed, motor_open)
    claw.run_target(claw_speed, motor_close)
    return

# drops brick into appropriate container
def sort(angle):
    sort_motor.run_target(sort_speed, angle)
    drop()
    sort_motor.run_target(sort_speed, cam_angle)
    wait(2000)
    return

# Write your program here
ev3.speaker.beep()
claw.run_angle(claw_speed,-100)
while True:
    shape = Get_SL("brickType")
    if shape == "0": # one X two brick detected
        sort(oneXtwo)
    elif shape == "1": # one x three brick detected
        sort(oneXthree)
    elif shape == "2": # two x two brick detected
        sort(twoXtwo)
    elif shape == "3": # two x three brick detected
        sort(twoXthree)
    elif shape == "4": # two x four brick detected
        sort(twoXfour)
    else:
        print("no brick detected")
    wait(1000)