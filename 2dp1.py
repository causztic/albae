import os
import glob
import time
from libdw import sm
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

FAN_0 = 23
FAN_1 = 24
GPIO.setup(FAN_0, GPIO.OUT)
GPIO.setup(FAN_1, GPIO.OUT)

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

optimal = 27


def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        # temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c


def setWaterPumpAndFan():
    fan_cw = GPIO.PWM(FAN_0, 1000)
    fan_cw.start(0)
    return fan_cw


class TemperatureSM(sm.SM):

    startState = "cold"

    def __init__(self):
        self.state = self.startState

    def getNextValues(self, state, inp):
        power = 0.5
        if inp > optimal:
            nextState = "hot"
        else:
            nextState = "cold"

        if state == "hot":
            power = 0.5
        elif state == "cold":
            power = 0

        print temperature, nextState
        return nextState, (power, power)

tsm = TemperatureSM()
f = setWaterPumpAndFan()
while (True):
    temperature = read_temp()
    f_power, wp_power = tsm.step(temperature)
    #wp.ChangeDutyCycle(wp_power * 100)
    f.ChangeDutyCycle(f_power * 100.0)
    time.sleep(1)
