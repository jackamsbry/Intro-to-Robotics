#!/usr/bin/env pybricks-micropython

from pybricks import ev3brick as brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import (Port, Stop, Direction, Button, Color,
                                 SoundFile, ImageFile, Align)
from pybricks.tools import print, wait, StopWatch
from pybricks.robotics import DriveBase
from passwords import Key as Key

import ubinascii, ujson, utime, urequests

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


def getQuote():
     urlVal = "http://api.kanye.rest/"
     headers ={"Accept":"application/json"}
     try:
          value = urequests.get(urlVal).text
          data = ujson.loads(value)
          result = data.get("quote")

     except Exception as e:
          print(e)
          result = "failed"
     return result

yeQuote = getQuote()

Put_SL("yeQuote", "STRING", yeQuote)

ultrasonic = UltrasonicSensor(Port.S1)
grabMotor = Motor(Port.B)

l_motor = Motor(Port.D, Direction.COUNTERCLOCKWISE)
r_motor = Motor(Port.A, Direction.COUNTERCLOCKWISE)

wheel_dia = 56
wheel_spacing = 164

driveBase = DriveBase(l_motor, r_motor, wheel_dia, wheel_spacing)

grabMotor.dc(0)
wasGrab = True
isGrab = True
Put_SL('isGrab','BOOLEAN', 'true')


init_search_dir = Get_SL('SearchDirection')
dist_thresh = 150
turn_thresh = 200
count = 0
best_dist = 5000
time_prev = 0

watch = StopWatch()
watch.pause()
watch.reset()

while True :
     isManual = Get_SL('ManualCtl')
     isManual = True if isManual == "true" else False
     if isManual:
          isGrab = Get_SL('isGrab')
          isGrab = True if isGrab == "true" else False
          driveCMD = Get_SL('driveCMD')
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

          ultDist = ultrasonic.distance()

          if driveCMD == '0' :
               driveBase.stop(Stop.BRAKE)
          elif driveCMD == '1' :
               driveBase.drive(100,0)
          elif driveCMD == '2' :
               driveBase.drive(10,45)
          elif driveCMD == '3' :
               driveBase.drive(10,-45)
          elif driveCMD == '4' :
               driveBase.drive(-100,0)
     else:
          ultDist = ultrasonic.distance() #Get distance from ultrasonic sensor
          if ultDist > dist_thresh:
               watch.resume()
               if watch.time() <= 1500:
                    driveBase.drive(100, 0)
               else:
                    if init_search_dir == '0':
                         turn_direction = -70
                         speed = 0
                    elif init_search_dir == '1':
                         turn_direction = 70
                         speed = 0
                    else:
                         turn_direction = 20
                         speed = 50
                    driveBase.drive(speed, turn_direction)
                    ultDist = ultrasonic.distance()
                    if ultDist < best_dist:
                         best_dist = ultDist
                         watch.pause()
                         watch.reset()