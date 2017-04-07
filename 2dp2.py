import os
import glob
import time

from functools import partial
from libdw import sm
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock

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

use_thermometer = True

try:
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')

    base_dir = '/sys/bus/w1/devices/'
    device_folder = glob.glob(base_dir + '28*')[0]
    device_file = device_folder + '/w1_slave'
except:
    print "Thermometer not detected!"
    use_thermometer = False


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

    def __init__(self):
        self.state = self.startState
        self._optimal = 27.0

    @property
    def optimal(self):
        return self._optimal

    @optimal.setter
    def set_optimal(self, value):
        self._optimal = float(value)


    def getNextValues(self, state, inp):
        power = 1.0
        nextState = "cold"
        if float(inp) > self.optimal:
            nextState = "hot"
        elif float(inp) < self.optimal:
            nextState = "cold"

        print nextState, self.optimal, inp

        if state == "hot":
            power = 1.0
        elif state == "cold":
            power = 0

        return nextState, (power, power)


class AlbaeApp(App):

    def system_temp_change(self, instance, value): self.updateGUI(value)

    def target_temp_change(self, instance, value): 
        self.tsm.optimal = float(value)
        self.updateGUI(self.system_temp.text)

    def plus_system_temp(self, instance):          self.change_system_temp(self.system_temp, 0.1)
    def minus_system_temp(self, instance):         self.change_system_temp(self.system_temp, -0.1)
    def plus_t_temp(self, instance):               self.change_system_temp(self.target, 0.1)
    def minus_t_temp(self, instance):              self.change_system_temp(self.target, -0.1)
    def change_system_temp(self, instance, value): instance.text = str(float(instance.text) + value)

    def __init__(self, **kwargs):
        App.__init__(self, **kwargs)
        self.tsm = TemperatureSM()
        self.fp = Label(text="0.0%")
        self.wpp = Label(text="0.0%")

        self.target = TextInput(text=str(self.tsm.optimal))
        self.target.bind(text=self.target_temp_change)
        self.increment_t_temp_btn = Button(on_press=self.plus_t_temp, text="+")
        self.decrement_t_temp_btn = Button(on_press=self.minus_t_temp, text="-")

        self.system_temp = TextInput(text=str(25.0))
        self.system_temp.bind(text=self.system_temp_change)
        self.increment_sys_temp_btn = Button(on_press=self.plus_system_temp, text="+")
        self.decrement_sys_temp_btn = Button(on_press=self.minus_system_temp, text="-")

        self.surr_temp = Label(
            text=read_temp() if use_thermometer else "Not detected")

    def build(self):

        main = GridLayout(cols=2)

        main.add_widget(Label(text="Target Temperature in Celsius"))

        tbox = BoxLayout(orientation="horizontal")
        tbox.add_widget(self.target)
        tbox.add_widget(self.increment_t_temp_btn)
        tbox.add_widget(self.decrement_t_temp_btn)
        main.add_widget(tbox)

        if not use_thermometer:
            main.add_widget(Label(text="Change the System Temperature"))

            box = BoxLayout(orientation="horizontal")
            box.add_widget(self.system_temp)
            box.add_widget(self.increment_sys_temp_btn)
            box.add_widget(self.decrement_sys_temp_btn)
            main.add_widget(box)

        main.add_widget(
            Label(text="Algae Temperature \n (if thermometer is detected)", halign="center"))
        main.add_widget(self.surr_temp)

        main.add_widget(Label(text="Fan Power"))
        main.add_widget(self.fp)

        main.add_widget(Label(text="Water Pump Power"))
        main.add_widget(self.wpp)
        if use_thermometer:
            Clock.schedule_interval(self.updateGUI(), 1)
        return main

    def updateGUI(self, temp=None):
        if not temp:
            temp = read_temp()
        fan_power, wp_power = self.tsm.step(temp)
        self.fp.text = str(fan_power*100) + "%"
        self.wpp.text = str(wp_power*100) + "%"

        if use_thermometer:
            self.surr_temp = str(temp)


if __name__ == '__main__':
    AlbaeApp(name="Albae").run()