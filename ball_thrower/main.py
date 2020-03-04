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

#Setup EV3 Devices
switchMotor = Motor(Port.B, Direction.COUNTERCLOCKWISE, [8, 24, 40])
loadMotor = Motor(Port.A, Direction.COUNTERCLOCKWISE, [16, 36])
distanceSensor = UltrasonicSensor(Port.S4)

#Define Constants 
#Distances in meters and masses in grams
ballOffsetx = -19/1000
ballOffsety = 152/1000
armRadius = 144/1000
cupHeight = 122/1000
cupRadius = 97/1000
armMass = 50
ballMass = 10

#Data for machine learning model
distData = [252, 191, 63, 44, 181, 154, 304, 237, 237, 326, 219, 190, 126, 112, 91, 120, 40, 44, 32, 147, 147, 203, 203, 233, 267, 199, 184, 137, 103, 149, 103, 219, 199, 199, 184, 184, 67, 76, 40, 158, 209, 288, 243, 199, 174, 166, 158, 164, 166, 139]
angleData = [118, 109, 90, 54, 108, 112, 164, 125, 129, 132, 93, 135, 94, 101, 74, 78, 70, 69, 66, 102, 79, 93, 132, 99, 136, 92, 93, 84, 81, 96, 58, 130, 114, 113, 108, 83, 49, 84, 76, 109, 140, 118, 111, 103, 114, 81, 107, 89, 94, 114]

#Functions to communicate with SystemLink
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

#Physics model functions
def newtonSpeed(dist, angle):
    angle_rad = math.radians(angle)
    dx = dist - ballOffsetx + cupRadius
    dy = cupHeight - ballOffsety
    speed = (3*math.sqrt(109/2)*dx*(1/math.cos(angle_rad)))/(10*math.sqrt(dx*math.tan(angle_rad)-dy))
     
    return speed
    
def momentumCalc(speed):
     epsilon = 0.7
     angle = math.acos(1-((((speed*(armMass+ballMass))/((1+epsilon)*armMass))**2)/(2*9.81*armRadius)))

     return angle

#Linear regression model using machine learning
def linearModel(learningRate, epochs, distData, angleData):
    m = 0
    b = 0
    L = learningRate
    x= []
    for i in range(len(angleData)):
        x.append(angleData[i]**2)
    y = distData
    numPoints = len(x)

    for i in range(epochs):
        y_pred = []
        dm = []
        db = []

        for j in range(numPoints):
            y_pred.append(m*x[j]+b) #Predicted y values
            dm.append(x[j] * (y[j]) - y_pred[j]) 
            db.append(y[j]-y_pred[j])
        
        D_m = (-2/numPoints) * sum(dm)
        D_b = (-2/numPoints) * sum(db)

        m = m - L * D_m
        b = b - L * D_b 
    #print(m)
    #print(b)  

    return [m, b]

#Main function
def main():
    releaseAngle = 35
    #Bring arm up before it hits the ball
    wasLaunch = False
    wasLoad = False
    iterations = 100
    
    

    #Create linear regression model using gradient descent
    ## Gradient Descent of linear regression model
    # learningRate = 1
    # epochs = 0
    # for i in range(iterations):
    #     learningRate /= 100
    #     for j in range(iterations):
    #         epochs += 1 
    #         model = linearModel(learningRate, epochs, distData, angleData)
    #         sumSquares =[]
    #         sumRes = []
    #         rSquared_max = 0
    #         for x in range(len(distData)):
    #             distMean = sum(distData)/len(distData)
    #             y_model = (model[0] * angleData[x]) + model[1]
    #             sumSquares.append((distData[x] - distMean)**2) 
    #             sumRes.append((distData[x] - y_model)**2) 
    #         sumSquares = sum(sumSquares)
    #         sumRes = sum(sumRes)
    #         rSquared = 1 - (sumRes/sumSquares)
    #         if rSquared > rSquared_max:
    #             rSquared_max = rSquared
    #             print(rSquared_max)
    #             model_max = model

    while True:
        isRegression = True if Get_SL("isRegression") == "true" else False
        if isRegression:
            total = 0
            #Find the average distance from several data points
            for value in range(10):
                dist = distanceSensor.distance()
                total += dist
            averageDist = total/10
            #Get control values from SL
            isLaunch = True if Get_SL("isLaunch") == "true" else False
            isLoad = True if Get_SL("isLoad") == "true" else False
            Put_SL("cupDistance", "STRING", str(averageDist))
            #Calculate required speed
            speed = newtonSpeed(averageDist, releaseAngle)
            Put_SL("ballSpeed", "STRING", str(speed))
            #armAngle = round(math.sqrt(abs((averageDist - model[1])/model[0])))
            #Calculate angle using linear regression model
            armAngle = round(math.sqrt(abs((averageDist - 47.006)/0.0112)))
            armHeight = armRadius - (armRadius * math.cos(armAngle))
            Put_SL("armHeight", "STRING", str(armHeight))
            #Bring the arm up to the correct height
            if isLaunch == False and isLoad == True and wasLoad == False:
                loadMotor.run_angle(300, round(armAngle), Stop.BRAKE)
                wasLoad = True

            #Release Arm
            if isLaunch == True and wasLaunch == False and isLoad == True:
                switchMotor.run_target(200, 70)
                wasLaunch = True
            
            #Engage clutch
            if isLaunch == False and wasLaunch == True and isLoad == False:
                switchMotor.run_target(200, 0)
                wasLaunch = False
                wasLoad = False

        else:
            total = 0
            #Find the average distance from several data points
            for value in range(10):
                dist = distanceSensor.distance()/1000
                total += dist
            averageDist = total/10
            #Get control values from SL
            isLaunch = True if Get_SL("isLaunch") == "true" else False
            isLoad = True if Get_SL("isLoad") == "true" else False
            Put_SL("cupDistance", "STRING", str(averageDist))
            #Calculate required speed
            speed = newtonSpeed(averageDist, releaseAngle)
            Put_SL("ballSpeed", "STRING", str(speed))
            #Calculate the reqired arm angle
            armAngle = momentumCalc(speed)
            #Scale values
            armAngle *= 1.8
            armHeight = armRadius - (armRadius * math.cos(armAngle))
            Put_SL("armHeight", "STRING", str(armHeight))

            #Bring the arm up to the correct height
            if isLaunch == False and isLoad == True and wasLoad == False:
                loadMotor.run_angle(300, round(math.degrees(armAngle)), Stop.BRAKE)
                wasLoad = True

            #Release arm
            if isLaunch == True and wasLaunch == False and isLoad == True:
                switchMotor.run_target(200, 60)
                wasLaunch = True
            
            #Engage clutch
            if isLaunch == False and wasLaunch == True and isLoad == False:
                switchMotor.run_target(200, 0)
                wasLaunch = False
                wasLoad = False
			
main()
