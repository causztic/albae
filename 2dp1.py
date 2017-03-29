import libdw.sm as sm
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

tempswitch = #where

GPIO.setup(tempswitch, GPIO.OUT)



class MySMClass(sm.SM):
    def __init__(self, GPIO.output(tempswitch, GPIO.HIGH)):
        self.temp = GPIO.output(tempswitch, GPIO.HIGH)
    if self.temp > :
        startState = 1
    else:
        startState = 0
    def getNextValues(self, state, inp):
        if state == 0:
            if self.temp > : #target temp
                return 1, (0.5, 0.5)
            return 0, (0, 0)
        if state == 1:
            if self.temp < : # target temp
                return 0, (0, 0)
            return 1, (0.5, 0.5)
