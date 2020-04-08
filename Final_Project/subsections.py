#! /usr/bin/python3

# The MIT License (MIT)
#
# Copyright (c) 2020 Jack Amsbry <jamsbry1@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""This file holds the all subclasses that make up the robot"""
from adafruit_servokit import ServoKit
import time, math
import numpy as np
from enum import IntEnum


class body(object):
    """this object holds all state information and computes inverse kinematics for robot body""" 
    BODYLENGTH = 209.55
    BODYWIDTH = 184.15
    BODYOFFSET = 12.7

    def __init__(self):
        """parameters of the robot body"""
        #initialize body position
        self.bodyPos_x = 0
        self.bodyPos_y = 0
        self.bodyPos_z = 0

        #initialize body rotation
        self.bodyRot_x = 0 #roll
        self.bodyRot_y = 0 #pitch
        self.bodyRot_z = 0 #yaw

        #gaits
        self.gaitIndex = 0
        self.gaitStep = 0
        self.gaits = [
           [(1, 0, 1, 0, 1, 0),\
            (0, 1, 0, 1, 0, 1)],\
            [(1, 0, 0, 0, 0, 1),\
            (0, 0, 1, 0, 1, 0),\
            (0, 1, 0, 1, 0, 0)],\
            [(1, 0, 0, 0, 0, 0),\
            (0, 1, 0, 0, 0, 0),\
            (0, 0, 1, 0, 0, 0),\
            (0, 0, 0, 1, 0, 0),\
            (0, 0, 0, 0, 1, 0),\
            (0, 0, 0, 0, 0, 1)]
        ]  #Tripod, Ripple, Wave
                        
        self.gaitCurrent = self.gaits[0] #Tripod is default gait

    def gaitSelect(self):
        if self.gaitIndex < 2:
            self.gaitIndex += 1
        else:
            self.gaitIndex = 0

        self.gaitCurrent = self.gaits[self.gaitIndex]

    def gaitIncrement(self):
        if self.gaitStep < (len(self.gaitCurrent)-1):
            self.gaitStep += 1
        else:
            self.gaitStep = 0

    def IKSolve(self):
        #x distance to front and back motors from center of body
        fbMotorDist = (self.BODYWIDTH/2) - self.BODYOFFSET
        mMotorDist = self.BODYWIDTH/2
        yDist = self.BODYLENGTH/2
        fbMotorRad = math.sqrt(fbMotorDist**2 + yDist**2)

        #Convert rotation angles to radians for calculations
        pitch = math.radians(self.bodyRot_x) #Rotation about x axis
        roll = math.radians(self.bodyRot_y) #Rotation about y axis
        yaw = math.radians(self.bodyRot_z) #Rotation about z axis

        #Change in x, y, z points of motors using rotation matrix
        lf = [fbMotorDist * math.cos(roll) + fbMotorRad * math.sin(yaw) - self.bodyPos_x,\
            yDist * math.cos(pitch) + fbMotorRad * math.cos(yaw) - self.bodyPos_y,\
            fbMotorDist * math.sin(roll) + yDist * math.sin(pitch) - self.bodyPos_z]
        lm = [mMotorDist * math.cos(roll) + mMotorDist * math.sin(yaw) - self.bodyPos_x,\
            yDist * math.cos(pitch) + mMotorDist * math.cos(yaw) - self.bodyPos_y,\
            mMotorDist * math.sin(roll) + yDist * math.sin(pitch) - self.bodyPos_z]
        lb = [fbMotorDist * math.cos(roll) + fbMotorRad * math.sin(yaw) - self.bodyPos_x,\
            -yDist * math.cos(pitch) + fbMotorRad * math.cos(yaw) - self.bodyPos_y,\
            fbMotorDist * math.sin(roll) + -yDist * math.sin(pitch) - self.bodyPos_z]

        rf = [-fbMotorDist * math.cos(roll) - fbMotorRad * math.sin(yaw) - self.bodyPos_x,\
            yDist * math.cos(pitch) - fbMotorRad * math.cos(yaw) - self.bodyPos_y,\
            -fbMotorDist * math.sin(roll) + yDist * math.sin(pitch) - self.bodyPos_z]
        rm = [mMotorDist * math.cos(roll) - mMotorDist * math.sin(yaw) - self.bodyPos_x,\
            yDist * math.cos(pitch) - mMotorDist * math.cos(yaw) - self.bodyPos_y,\
            mMotorDist * math.sin(roll) + yDist * math.sin(pitch) - self.bodyPos_z]
        rb = [-fbMotorDist * math.cos(roll) - fbMotorRad * math.sin(yaw) - self.bodyPos_x,\
            -yDist * math.cos(pitch) - fbMotorRad * math.cos(yaw) - self.bodyPos_y,\
            -fbMotorDist * math.sin(roll) + -yDist * math.sin(pitch) - self.bodyPos_z]

        dLegs = [lf, lm, lb, rf, rm, rb]

        return dLegs


class hexleg(object):
    """object to calculate inverse kinematics for 3dof hexapod leg and control servo motion"""
    #Leg Section lengths in mm
    TIBIA_LENGTH = 193.68
    FEMUR_LENGTH = 127.47
    COXA_LENGTH = 83

    def __init__(self, legIndex, ServoKit, isInverted=False):
        self.legIndex = legIndex
        #Set initial values for robot startup
        self.a_coxa = 90
        self.a_femur = 180
        self.a_tibia = 90
        self.isInverted = isInverted
        self.path = "none"
        self.a_coxa_new = 0
        self.a_femur_new = 0
        self.a_tibia_new = 0
        
        #Put each servos index on the servo driver into a list
        if isInverted:
            self.servo_index = [self.legIndex*3, self.legIndex*3 + 1, self.legIndex*3 + 2]
        else:
            self.servo_index = [(self.legIndex-3)*3, (self.legIndex-3)*3 + 1, (self.legIndex-3)*3 + 2]

        #Move servos to initial position
        self.coxa_servo = ServoKit.servo[self.servo_index[0]]
        self.femur_servo = ServoKit.servo[self.servo_index[1]]
        self.tibia_servo = ServoKit.servo[self.servo_index[2]]
        self.servos = [self.coxa_servo, self.femur_servo, self.tibia_servo]

        #Initialize variables for inverse kinematics
        self.x, self.y, self.z = self.FKSolve(self.a_coxa, self.a_femur, self.a_tibia)

        self.x_new = 0
        self.y_new = 0
        self.z_new = 0
        self.x_init = 0
        self.y_init = 0
        self.z_init = 0

        self.run_angle(self.a_coxa, 0)
        self.run_angle(self.a_femur, 1)
        self.run_angle(self.a_tibia, 2)
        time.sleep(.25)

    def FKSolve(self, a_coxa, a_femur, a_tibia):
        """Forward kinematics calculation to find location of leg tip. Angles are given in degrees"""
        #temporary angle for calculation
        temp_ang = a_tibia - (90 - (a_femur - 90))
        
        #Convert to radians
        a_coxa = math.radians(a_coxa)
        a_femur = math.radians(a_femur - 90)
        temp_ang = math.radians(temp_ang)
        x = (self.COXA_LENGTH + (self.FEMUR_LENGTH * math.cos(a_femur)) + (self.TIBIA_LENGTH *math.sin(temp_ang))) * math.cos(a_coxa)
        y = (self.COXA_LENGTH + (self.FEMUR_LENGTH * math.cos(a_femur)) + (self.TIBIA_LENGTH *math.sin(temp_ang))) * math.sin(a_coxa)
        z = (self.TIBIA_LENGTH * math.cos(temp_ang)) - (self.FEMUR_LENGTH * math.sin(a_femur))  
        return x, y, z

    def IKSolve(self, x, y, z):
        #equations taken from blog post by user downeym here: https://www.robotshop.com/community/forum/t/inverse-kinematic-equations-for-lynxmotion-3dof-legs/21336
        try:
            legLength = math.sqrt(x**2 + y**2)
            HF = math.sqrt((legLength - self.COXA_LENGTH)**2 + z**2)
            A1 = math.atan2(legLength - self.COXA_LENGTH, z)
            A2 = math.acos((self.TIBIA_LENGTH**2 - self.FEMUR_LENGTH**2 - HF**2)/(-2 * self.FEMUR_LENGTH * HF))
            B1 = math.acos((HF**2 - self.TIBIA_LENGTH**2 - self.FEMUR_LENGTH**2)/(-2 * self.FEMUR_LENGTH * self.TIBIA_LENGTH))
            C1 = math.atan2(y, x)
            
            #Convert to servo reference frame and solve for final angles
            a_coxa = math.degrees(C1)
            a_femur = math.degrees(A1 + A2) 
            a_tibia = math.degrees(B1)

            return a_coxa, a_femur, a_tibia
        except Exception as e:
            print(e)
            return self.a_coxa, self.a_femur, self.a_tibia
        
    def run_angle(self, move_angle, servo_index):
        """Runs to a target angle for a given servo"""
        if self.isInverted:
            new_angle = 180 - move_angle
        else:
            new_angle = move_angle
        try:
            if servo_index == 0:
                self.a_coxa = move_angle
            elif servo_index == 1:
                self.a_femur = move_angle
            else:
                self.a_tibia = move_angle
            self.servos[servo_index].angle = new_angle
        except:
            print("Failed to move by {} degrees".format(move_angle))

    def run_position(self, x, y, z):
        a_coxa, a_femur, a_tibia = self.IKSolve(x, y, z)
        self.run_angle(a_coxa, 0)
        self.run_angle(a_femur, 1)
        self.run_angle(a_tibia, 2)