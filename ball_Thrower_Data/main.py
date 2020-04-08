#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
import utime

# Write your program here
ev3 = EV3Brick()
ev3.speaker.beep()

switchMotor = Motor(Port.B, Direction.COUNTERCLOCKWISE, [8, 24, 40])
loadMotor = Motor(Port.A, Direction.COUNTERCLOCKWISE, [16, 36])

distanceSensor = UltrasonicSensor(Port.S4)
btn = TouchSensor(Port.S1)
resetBtn = TouchSensor(Port.S2)
time = StopWatch()
distData = []
angleData = []

def main():

    while True:
        dist = distanceSensor.distance()
        angle = loadMotor.angle()

        if resetBtn.pressed():
            time.resume()
            print("Shooting Ball!")
            switchMotor.run_target(200, 60)
            time.reset()
            while (not btn.pressed()) and (time.time() < 5000):
                wait(10)
                print("Waiting for Button Press...")
            else:
                time.pause()
                if btn.pressed():
                    distData.append(dist)
                    angleData.append(angle)
                    print("Data point added")
                    wait(5000 - time.time())
                else:
                    print("Wait Timed out")

            switchMotor.run_target(200, 0)
            loadMotor.reset_angle(0)

        if len(distData) == 50:
            break

    print(distData)
    print(angleData)

main()