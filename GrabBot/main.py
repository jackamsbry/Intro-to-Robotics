#!/usr/bin/env pybricks-micropython

from pybricks import ev3brick as brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import (Port, Stop, Direction, Button, Color,
                                 SoundFile, ImageFile, Align)
from pybricks.tools import print, wait, StopWatch
from pybricks.robotics import DriveBase

import ubinascii, ujson, urequests, utime
     
Key = 'w-TANbEa0fhalpKtCPNGF0Zuuc6J3r9st6-FSUv55v'
     
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


ultrasonic = UltrasonicSensor(Port.S1)
grabMotor = Motor(Port.B)

l_motor = Motor(Port.D, Direction.COUNTERCLOCKWISE)
r_motor = Motor(Port.A, Direction.COUNTERCLOCKWISE)
driveBase = DriveBase(l_motor, r_motor, 56, 164)

grabMotor.dc(0)
wasGrab = False

while True :
     isGrab = Get_SL('isGrab')
     isGrab = True if isGrab == "true" else False
     isDrive = Get_SL('isDrive')
     isDrive = True if isDrive == "true" else False
     if isGrab == True and wasGrab == False:
          grabMotor.dc(100)
          wait(2000)
          grabMotor.dc(0)
          wasGrab = isGrab
     
     if isGrab == False and wasGrab == True:
          grabMotor.dc(-100)
          wait(2000)
          grabMotor.dc(0)
          wasGrab = isGrab

     if isDrive == True :
          driveBase.drive(250,0)
     elif isDrive == False :
          driveBase.drive(0, 0)


               
          
          
          
          

    
