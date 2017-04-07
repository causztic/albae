import os
import glob
import time

from libdw import sm
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
# import RPi.GPIO as GPIO

# GPIO.setmode(GPIO.BCM)

# GPIOS

# WATER_PUMP1 = 23
# WATER_PUMP2 = 24

# FAN_1 = 17
# FAN_2 = 27

# GPIO.setup(WATER_PUMP1, GPIO.OUT)
# GPIO.setup(WATER_PUMP2, GPIO.OUT)
# GPIO.setup(FAN_1, GPIO.OUT)
# GPIO.setup(FAN_2, GPIO_OUT)

# os.system('modprobe w1-gpio')
# os.system('modprobe w1-therm')

# base_dir = '/sys/bus/w1/devices/'
# device_folder = glob.glob(base_dir + '28*')[0]
# device_file = device_folder + '/w1_slave'

# optimal = 27


# def read_temp_raw():
#     f = open(device_file, 'r')
#     lines = f.readlines()
#     f.close()
#     return lines


# def read_temp():
#     lines = read_temp_raw()
#     while lines[0].strip()[-3:] != 'YES':
#         time.sleep(0.2)
#         lines = read_temp_raw()
#     equals_pos = lines[1].find('t=')
#     if equals_pos != -1:
#         temp_string = lines[1][equals_pos + 2:]
#         temp_c = float(temp_string) / 1000.0
#         # temp_f = temp_c * 9.0 / 5.0 + 32.0
#         return temp_c


# def setWaterPumpAndFan():
#     wp_cw = GPIO.PWM(WATER_PUMP1, 1000)
#     # wp_cw2  = GPIO.PWN(WATER_PUMP2, 1000) unused
#     fan_cw = GPIO.PWM(FAN_1, 1000) unused
#     # fan_cw2 = GPIO.PWN(FAN_2, 1000) unused
#     wp_cw.start(0)
#     # wp_cw2.start(0)
#     fan_cw.start(0)
#     # fan_cw2.start(0)

#     return wp_cw, fan_cw


class TemperatureSM(sm.SM):

    startState = "cold"
    k = 1
    optimal = 27
    def getNextValues(self, state, inp):
        power = 1.0
        nextState = "cold"
        if inp > self.optimal:
            nextState = "hot"

        if state == "hot":
            power = 1.0
        elif state == "cold":
            power = 0

        return nextState, (power, power)

class MainWindow(GridLayout):
    pass

class AlbaeApp(App):

    def build(self):
        tsm = TemperatureSM()
        main = GridLayout(col=2)
        main.add_widget(Label(text="Target Temperature in Celsius"))
        target = TextInput()
        main.add_widget(target)
        return main

if __name__ == '__main__':
    AlbaeApp(name="Albae").run()
