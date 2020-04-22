#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
import math, urequests, ujson, ubinascii, utime
from passwords import Key1, Key2
# Write your program here
ev3 = EV3Brick()
ev3.speaker.beep()

#SystemLink Functions
def SL_setup(Key):
     urlBase = "https://api.systemlinkcloud.com/nitag/v2/tags/"
     headers = {"Accept":"application/json","x-ni-api-key":Key}
     return urlBase, headers
     
def Put_SL(Tag, Type, Value, Key):
     urlBase, headers = SL_setup(Key)
     urlValue = urlBase + Tag + "/values/current"
     propValue = {"value":{"type":Type,"value":Value}}
     try:
          reply = urequests.put(urlValue,headers=headers,json=propValue).text
     except Exception as e:
          print(e)         
          reply = 'failed'
     return reply

def Get_SL(Tag, Key):
     urlBase, headers = SL_setup(Key)
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
     
def Create_SL(Tag, Type, Key):
     urlBase, headers = SL_setup(Key)
     urlTag = urlBase + Tag
     propName={"type":Type,"path":Tag}
     try:
          urequests.put(urlTag,headers=headers,json=propName).text
     except Exception as e:
          print(e)

#Arm class
class robotArm():
    BASEHEIGHT = 95.25
    LOWERLENGTH = 133.35 
    UPPERLENGTH = 222.25
    BASEOFFSET = 63.5

    def __init__(self, base, shoulder, elbow, claw):
        self.base = base
        self.shoulder = shoulder
        self.elbow = elbow
        self.claw = claw

        self.x = 0
        self.y = 0
        self.z = 0
        self.clawAngle = 0

    def FKSolve(self):
        x = (self.LOWERLENGTH * math.sin(self.shoulder.angle()) + self.UPPERLENGTH * math.sin(self.elbow.angle()) + self.BASEOFFSET) * math.cos(self.base.angle())
        y = (self.LOWERLENGTH * math.sin(self.shoulder.angle()) + self.UPPERLENGTH * math.sin(self.elbow.angle()) + self.BASEOFFSET) * math.sin(self.base.angle())
        z = self.BASEHEIGHT + (self.LOWERLENGTH * math.cos(self.shoulder.angle())) + self.UPPERLENGTH * math.cos(self.elbow.angle())
        clawAngle = self.shoulder.angle() + self.elbow.angle()
        return x, y, z, clawAngle

    def IKSolve(self, x, y, z):
        try:
            z += self.BASEHEIGHT
            armLength = math.sqrt(x**2 + y**2)
            shoulderClawDist = math.sqrt((armLength - self.BASEOFFSET)**2 + z**2)
            A1 = math.atan2((armLength - self.BASEOFFSET), z)
            A2 = math.acos((self.UPPERLENGTH**2 - self.LOWERLENGTH**2 -shoulderClawDist**2)/(-2 * self.LOWERLENGTH * shoulderClawDist))
            B1 = math.acos((shoulderClawDist**2 - self.UPPERLENGTH**2 - self.LOWERLENGTH**2)/(-2 * self.UPPERLENGTH * self.LOWERLENGTH))

            A1 = math.degrees(A1)
            A2 = math.degrees(A2)
            B1 = math.degrees(B1)

            baseAngle = math.degrees(math.atan2(y, x))
            baseAngle = baseAngle if baseAngle > 45 else 45
            lowerAngle = 180 - (A1 + A2)
            upperAngle = 180 - B1
            return baseAngle, lowerAngle, upperAngle
        except Exception as e:
            print(e)
            print("Inverse Kinematics Failed")
            return self.base.angle(), self.shoulder.angle(), self.elbow.angle()
            
    def run_position(self, speed, x, y, z):
        # init_baseAngle, init_lowerAngle, init_upperAngle = self.IKSolve(self.x, self.y, self.z)
        baseAngle, lowerAngle, upperAngle = self.IKSolve(x, y, z)

        # dThetaBase = round(1/(abs(init_baseAngle - baseAngle)/10), 3)
        # dThetaLower = round(1/(abs(init_lowerAngle - lowerAngle)/10), 3)
        # dThetaUpper = round(1/(abs(init_upperAngle - upperAngle)/10), 3)
        # dThetaBase = 0.5 if dThetaBase == 0 else dThetaBase
        # dThetaLower = 0.5 if dThetaLower == 0 else dThetaLower
        # dThetaUpper = 0.5 if dThetaUpper == 0 else dThetaUpper 
        # print(dThetaBase, dThetaLower, dThetaUpper)
        self.base.run_target(speed, baseAngle, stop_type=Stop.BRAKE,  wait=False)
        self.shoulder.run_target(speed, lowerAngle, stop_type=Stop.BRAKE,  wait=False)
        self.elbow.run_target(speed, upperAngle, stop_type=Stop.BRAKE)
        self.x = x
        self.y = y
        self.z = z

    def grab(self):
        self.claw.dc(25)
        wait(200)

    def release(self):
        self.claw.dc(-25)
        wait(200)


# def record_moves(arm, button):
#     base = []
#     shoulder = []
#     elbow = []
#     while not button.pressed():
#         base.append(arm.base.angle())
#         shoulder.append(arm.shoulder.angle())
#         elbow.append(arm.elbow.angle())
#     angles=[base, shoulder, elbow]

def main():
    baseMotor = Motor(Port.A, Direction.CLOCKWISE, [12, 36])
    shoulderMotor = Motor(Port.B, Direction.COUNTERCLOCKWISE, [8, 40])
    elbowMotor = Motor(Port.C, Direction.COUNTERCLOCKWISE, [8, 40])
    clawMotor = Motor(Port.D)
  
    
    baseMotor.reset_angle(90)
    shoulderMotor.reset_angle(-23)
    elbowMotor.reset_angle(75)

    arm = robotArm(baseMotor, shoulderMotor, elbowMotor, clawMotor)

    arm.run_position(10, 245, 0, 25)
    print(arm.base.angle())
    print(arm.shoulder.angle())
    print(arm.elbow.angle())
    moveArm = True if Get_SL("moveArm", Key1) == "true" else False
    while not moveArm:
        wait(10)
        moveArm = True if Get_SL("moveArm", Key1) == "true" else False
        print(arm.base.angle())
        print(arm.shoulder.angle())
        print(arm.elbow.angle())
    else:
        arm.run_position(7, -266.7, 0, 125)
        wait(500)
        arm.grab()
        wait(500)
        arm.run_position(7, 0, 266.7, 114.3)
        wait(500)
        arm.release()
        if dist.distance() < 80:
            Put_SL("Start05", "BOOLEAN", "false", Key2)
            #Put_SL("Start06", "BOOLEAN", "true")

main()