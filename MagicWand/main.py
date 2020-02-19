#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

# Write your program here
ev3 = EV3Brick()
ev3.speaker.beep()

# '''
# This reads the USB serial line on the EV3 as fast as possible
# and assumes that data is coming from the Arduino much faster
# than we can read it - so it grabs all the data, splits it up into an array,
# and then takes the second to last element of that array to get an
# array of accelerations and angular accelerations.
# The 6 elements are:
#      x acceleration
#      y acceleration
#      z acceleration
#      x gyro
#      y gyro
#      z gyro
     
# Note that I take the second to last line because the last line might be incomplete
# (who knows where in the serial transmission the line is when I do the read).
# '''

imumeans = [0, 0, 0, 0, 0, 0]
threshold = [120, 120, 120]
button = TouchSensor(Port.S1)

import serial
s=serial.Serial("/dev/ttyACM0",9600)
while True:
    if button.pressed() == True:
        count = 0
        while button.pressed() == True:
            data=s.read(s.inWaiting()).decode("utf-8")
            if len(data) != 0:
                data = data.splitlines()
                imu = data[0].split(',')
                if imu == ['']:
                    continue
                try:  
                    for i in range(len(imu)):
                        imu[i] = float(imu[i])
                        #print(imu)

                    for means in range(len(imumeans)):
                        imumeans[means] = (imumeans[means]+imu[means])
                        #print(imumeans)
                    count = count+1

                except Exception as errmsg:
                    print(errmsg)

        print('buttonwaspressed')

        for k in range(len(imumeans)):
            imumeans[k] = imumeans[k]/count

        # First check positive rotation
        if ((abs(imumeans[3]) > threshold[0]) and (imumeans[3] > 0)):
            ev3.speaker.beep(261, 500)
        elif ((abs(imumeans[4]) > threshold[1]) and (imumeans[4] > 0)):
            ev3.speaker.beep(220, 500)
        elif ((abs(imumeans[5]) > threshold[2]) and (imumeans[5] > 0)):
            ev3.speaker.beep(196, 500)
        # Then check negative rotation
        elif ((abs(imumeans[3]) > threshold[0]) and (imumeans[3] < 0)):
            ev3.speaker.beep(330, 500)
        elif ((abs(imumeans[4]) > threshold[1]) and (imumeans[4] < 0)):
            ev3.speaker.beep(147, 500)
        elif ((abs(imumeans[5]) > threshold[2]) and (imumeans[5] < 0)):
            ev3.speaker.beep(294, 500)



        print(imumeans)

        
