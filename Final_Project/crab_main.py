#! /usr/bin/python3

from adafruit_servokit import ServoKit
import time, math, copy, requests, json, binascii
import numpy as np
from scipy.interpolate import CubicSpline
from subsections import hexleg, body

#SYSTEMLINK FUNCTIONS

Key = "bvd8X9LweQY9o2eP1NYL-p8mLL9wMAk6YYOnYSiIo0"

def SL_setup():
    urlBase = "https://api.systemlinkcloud.com/nitag/v2/tags/"
    headers = {"Accept":"application/json","x-ni-api-key":Key}
    return urlBase, headers
     
def Put_SL(Tag, Type, Value):
    urlBase, headers = SL_setup()
    urlValue = urlBase + Tag + "/values/current"
    propValue = {"value":{"type":Type,"value":Value}}
    try:
        reply = requests.put(urlValue,headers=headers,json=propValue).text
    except Exception as e:
        print(e)         
        reply = 'failed'
    return reply

def Get_SL(Tag):
    urlBase, headers = SL_setup()
    urlValue = urlBase + Tag + "/values/current"
    try:
        value = requests.get(urlValue,headers=headers).text
        data = json.loads(value)
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
        requests.put(urlTag,headers=headers,json=propName).text
    except Exception as e:
        print(e)

class bezier2d():
    def __init__(self):
        self.xpoints = []
        self.ypoints = []

    def addPoint(self, x, y):
        self.xpoints.append(x)
        self.ypoints.append(y)

    def editPoint(self, x, y, pointNum):
        self.xpoints[pointNum] = x
        self.ypoints[pointNum] = y

    def getPos(self, t):
        x = copy.deepcopy(self.xpoints)
        y = copy.deepcopy(self.ypoints)

        numPoints = len(self.xpoints)
        for i in range(numPoints-1):
            for j in range(numPoints-i-1):
                x[j] = (1-t)*x[j] + t*x[j+1]
                y[j] = (1-t)*y[j] + t*y[j+1]
        position = [x[0], y[0]]
        return position

class crabbot():
    MINTURNRAD = 609.6/2

    def __init__(self, legs, body, debug=False):
        self.legs = legs
        self.body = body

        self.moveCurve = bezier2d()
        self.pushCurve = bezier2d()
        self.wakeCurve = bezier2d()

        self.curve_init()

        self.turnRad = 100000 #Large number so effectively straight motion for default direction

        #State variables
        self.wasMoving = False
        self.isMoving = False

        #Debugging?
        self.debug = debug
    
    def interpolate_time(self, speed, numSteps):
            """interpolates between two delay times for smooth movement using cubic spline intrpolation"""
            time_steps = [0, numSteps/2, numSteps]
            delay_time = [0.05*speed, 0.01*speed, 0.05*speed]
            delayInterpolation = CubicSpline(time_steps, delay_time)
            delay_time = []
            for n in range(numSteps):
                delay_time.append(delayInterpolation(n))
            return delay_time

    def interpolate_step(self, speed, numPoints=100):
        """Interpolates between motors for smooth movement for a single gait step"""
        gait = self.body.gaitCurrent
        numSteps = len(gait)
        stepCurrent = gait[self.body.gaitStep]

        delayTime = self.interpolate_time(speed, numPoints)

        move_t = np.linspace(0, 1, num=numPoints)
        t = np.linspace(0,(1/(numSteps-1)), num=numPoints)
        move_pos = []
        push_pos = []
        for x in move_t:
            move_pos.append(self.moveCurve.getPos(x))
        
        for x in t:
            push_pos.append(self.pushCurve.getPos(x))

        self.isMoving = True
        
        for i in range(numPoints):
            for index, leg in enumerate(self.legs):
                
                if stepCurrent[index] == 1:
                    current_pos = move_pos[i]

                elif stepCurrent[index] == 0:
                    current_pos = push_pos[i]
                if not self.wasMoving:
                    leg.run_position(current_pos[0], leg.y_init, current_pos[1])

                leg.x_new = leg.x_init - current_pos[0]
                leg.y_new = leg.y_init 
                leg.z_new = leg.z_init - current_pos[1]

                #Body inverse kinematics
                # dLegs = self.body.IKSolve()
                # dLeg = dLegs[index]
                
                #Update leg position with body transformations
                # leg.x_new += dLeg[0]
                # leg.y_new += dLeg[1]
                # leg.z_new += dLeg[2]
                
                #Inverse kinematic calculation for leg position
                a_coxa, a_femur, a_tibia = leg.IKSolve(leg.x_new, leg.y_new, leg.z_new)
                
                #Run the servos to calculated angles
                leg.run_angle(a_coxa, 0)
                leg.run_angle(a_femur, 1)
                leg.run_angle(a_tibia, 2)   
                

                leg.a_coxa = a_coxa
                leg.a_femur = a_femur
                leg.a_tibia = a_tibia

                self.wasMoving = True
                time.sleep(0.002)
            time.sleep(0.002)
        for leg in self.legs:
            leg.x = leg.x_new
            leg.y = leg.y_new
            leg.z = leg.z_new
        
        
        self.isMoving = False

    def interpolate_angle(self, speed, numSteps, joint, angle):
        delayTime = self.interpolate_time(speed, numSteps)

        for leg in self.legs:   
            if joint == 0:
                leg.a_coxa_new = angle
                angles = np.linspace(leg.a_coxa, leg.a_coxa_new, numSteps)
                leg.a_coxa = leg.a_coxa_new
            elif joint == 1:
                leg.a_femur_new = angle
                angles = np.linspace(leg.a_femur, leg.a_femur_new, numSteps)
                leg.a_femur = leg.a_femur_new
            else:
                leg.a_tibia_new = angle
                angles = np.linspace(leg.a_tibia, leg.a_tibia_new, numSteps)
                leg.a_tibia = leg.a_tibia_new

        for i in range(numSteps):
            for leg in legs:
                if joint == 0:
                    leg.run_coxa_angle(angles[i])
                elif joint == 1:
                    leg.run_femur_angle(angles[i])
                else:
                    leg.run_tibia_angle(angles[i])
                time.sleep(delayTime[i])

    def curve_init(self):
        x0 = 50
        x1 = 2.5 * x0
        y = 250
        self.moveCurve.addPoint(x0, 0)
        self.moveCurve.addPoint(x1, 0)
        self.moveCurve.addPoint(0, y)
        self.moveCurve.addPoint(-x1, 0)
        self.moveCurve.addPoint(-x0, 0)

        self.pushCurve.addPoint(-x0, 0)
        self.pushCurve.addPoint(x0, 0)

    def stand(self):
        numPoints = 20
        startAngle = 60
        
        self. isMoving = True
        for i in range(numPoints):
            for index, leg in enumerate(self.legs):
                if index < 3:
                    leg.a_coxa_new = startAngle + index * 30
                else:
                    leg.a_coxa_new = startAngle + (index - 3) * 30
                leg.a_femur_new = 120
                leg.a_tibia_new = 50
                coxa_angles = np.linspace(leg.a_coxa, leg.a_coxa_new, num=numPoints)
                femur_angles = np.linspace(leg.a_femur, leg.a_femur_new, num=numPoints)
                tibia_angles = np.linspace(leg.a_tibia, leg.a_tibia_new, num=numPoints)
                    
                #Run the servos to calculated angles
                leg.run_angle(coxa_angles[i], 0)
                leg.run_angle(femur_angles[i], 1)
                leg.run_angle(tibia_angles[i], 2)
                leg.x_init, leg.y_init, leg.z_init = leg.FKSolve(leg.a_coxa_new, leg.a_femur_new, leg.a_tibia_new)
                leg.a_coxa = leg.a_coxa_new
                leg.a_femur = leg.a_femur_new
                leg.a_tibia = leg.a_tibia_new
                time.sleep(0.005)   
            time.sleep(0.1)
                

    def sit(self, numPoints = 25):
        #Calculate leg end positions
        pass

if __name__ == "__main__":
    """Main function for testing servo movement and gaits"""
    #Instantiate servo class for each PCA9685 board
    left_servos = ServoKit(channels=16, address=0x60)
    right_servos = ServoKit(channels=16, address=0x40)

    #Instantiate legs
    lf = hexleg(0, left_servos, isInverted=True)
    lm = hexleg(1, left_servos, isInverted=True)
    lb = hexleg(2, left_servos, isInverted=True)

    rf = hexleg(3, right_servos)
    rm = hexleg(4, right_servos)
    rb = hexleg(5, right_servos)

    legs = [lf, lm, lb, rf, rm, rb]
    
    #Instantiate body
    body = body()

    #Instantiate robot control class
    bot = crabbot(legs, body, debug=True)
    #Wait for 1.5 seconds so servos are in correct location
    time.sleep(1.5)
    #Set initial leg positions
    bot.stand()
    time.sleep(2.5)
    moveCMD = False
    while not moveCMD:
        time.sleep(0.01)
        moveCMD = True if (Get_SL("Start05") == "true") else False
    else:
        for i in range(6):
            bot.interpolate_step(1)
            bot.body.gaitIncrement()
   