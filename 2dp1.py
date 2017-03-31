import os
import glob
import time
from libdw import sm
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

# GPIOS

WATER_PUMP1 = 23
WATER_PUMP2 = 24

FAN_1 = 17
FAN_2 = 27

GPIO.setup(WATER_PUMP1, GPIO.OUT)
GPIO.setup(WATER_PUMP2, GPIO.OUT)
GPIO.setup(FAN_1, GPIO.OUT)
GPIO.setup(FAN_2, GPIO_OUT)

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
    wp_cw = GPIO.PWM(WATER_PUMP1, 1000)
    # wp_cw2  = GPIO.PWN(WATER_PUMP2, 1000) unused
    fan_cw = GPIO.PWM(FAN_1, 1000) unused
    # fan_cw2 = GPIO.PWN(FAN_2, 1000) unused
    wp_cw.start(0)
    # wp_cw2.start(0)
    fan_cw.start(0)
    # fan_cw2.start(0)
    
    return wp_cw, fan_cw


class TemperatureSM(sm.SM):

    startState = "cold"

    def __init__(self):
        self.state = self.startState

    def getNextValues(self, state, inp):
        power = 1.0
        if inp > optimal:
            nextState = "hot"
        else:
            nextState = "cold"

        if state == "hot":
            power = 1.0
        elif state == "cold":
            power = 0

        print temperature, nextState
        return nextState, (power, power)

tsm = TemperatureSM()
f = setWaterPumpAndFan()
while (True):
    temperature = read_temp() # read temperature from function
    wp_power, f_power = tsm.step(temperature) # step with temperature, get the power
    f.ChangeDutyCycle(f_power * 100) # convert the power to 0 to 100 for duty cycle
    wp.ChangeDutyCycle(wp_power * 100.0) # convert the power to a range of 0 to 100 for duty cycle
    time.sleep(1) # check every 1 second
