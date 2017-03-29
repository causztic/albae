import libdw.sm as sm
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

tempswitch = "4"
optimal = 30
GPIO.setup(tempswitch, GPIO.OUT)


class MySMClass(sm.SM):
    startState = "nice"
    
    def getNextValues(self, state, inp):
        temperature = GPIO.input(tempswitch)
        print temperature
        nextState = "nice"
        if temperature > optimal:
            nextState = "hot"
        elif temperature < optimal:
            nextState = "cold"
        return nextState, ""
