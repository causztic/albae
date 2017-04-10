'''
PART 2.1

We decided to use the Proportional-Derivative controller so that we are able to detect sudden temperature changes
in the algae, and increase the fan and water pump's power accordingly.

The function is in the form:
power = k0 * abs(optimal - current) + k1 * [ abs(optimal - current) - abs(optimal - previous) ], and scaled from 0 to 1.

k0 is 1 while k1 is 2.
This is because the rate of change is more crucial to regulating the temperature of the algae culture, to protect
it from sudden increase in surrounding temperature.

'''


import os
import glob
import time

from functools import partial
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock

from temperature_sm import TemperatureSM

use_thermometer = True

# attempt to detect Thermometer for use with GUI.
# if Thermometer not detected, use manual temperature input.
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
    """ Read the temperature raw."""
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp():
    """ convert the raw input into celsius. """
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

class AlbaeApp(App):
    """ Main GUI App. """
    def plus_system_temp(self, instance):
        """Add to system temperature by 0.1"""
        self.change_system_temp(self.system_temp, 0.1)

    def minus_system_temp(self, instance):
        """Decrease system temperature by 0.1"""
        self.change_system_temp(self.system_temp, -0.1)

    def plus_t_temp(self, instance):
        """increase target temperature by 0.1"""
        self.change_system_temp(self.target, 0.1)

    def minus_t_temp(self, instance):
        """decrease target temperature by 0.1"""
        self.change_system_temp(self.target, -0.1)

    def change_system_temp(self, instance, value):
        """ update text """
        instance.text = str(float(instance.text) + value)

    def __init__(self, **kwargs):
        App.__init__(self, **kwargs)
        self.tsm = TemperatureSM()
        self.fp = Label(text="0.0%")
        self.wpp = Label(text="0.0%")

        self.target = TextInput(text=str(self.tsm.optimal))
        self.increment_t_temp_btn = Button(on_press=self.plus_t_temp, text="+")
        self.decrement_t_temp_btn = Button(
            on_press=self.minus_t_temp, text="-")

        self.system_temp = TextInput(text=str(25.0))
        self.increment_sys_temp_btn = Button(
            on_press=self.plus_system_temp, text="+")
        self.decrement_sys_temp_btn = Button(
            on_press=self.minus_system_temp, text="-")

        self.surr_temp = Label(
            text=str(read_temp()) if use_thermometer else "Not detected")

    def build(self):
        # build the main layout
        main = GridLayout(cols=2)

        main.add_widget(Label(text="Target Temperature in Celsius"))

        tbox = BoxLayout(orientation="horizontal")
        tbox.add_widget(self.target)
        tbox.add_widget(self.increment_t_temp_btn)
        tbox.add_widget(self.decrement_t_temp_btn)
        main.add_widget(tbox)

        if not use_thermometer:
            # if thermometer not detected, use the manual controls.
            main.add_widget(Label(text="Change the System Temperature"))

            box = BoxLayout(orientation="horizontal")
            box.add_widget(self.system_temp)
            box.add_widget(self.increment_sys_temp_btn)
            box.add_widget(self.decrement_sys_temp_btn)
            main.add_widget(box)

            # use clock to check for system_temp updates instead of on_text
            Clock.schedule_interval(
                partial(self.updateGUI, self.system_temp), 1)

        main.add_widget(
            Label(text="Algae Temperature \n (if thermometer is detected)", halign="center"))
        main.add_widget(self.surr_temp)

        main.add_widget(Label(text="Fan Power"))
        main.add_widget(self.fp)

        main.add_widget(Label(text="Water Pump Power"))
        main.add_widget(self.wpp)

        if use_thermometer:
            # if thermometer is detected,
            # use clock to check for system_temp updates instead of on_text
            Clock.schedule_interval(
                partial(self.updateGUI), 1)

        return main

    def updateGUI(self, temp=None):
        """ Update GUI based on state machine."""
        self.tsm.optimal = float(self.target.text)
        temp = float(read_temp()) if use_thermometer else float(temp.text)

        fan_power, wp_power = self.tsm.step(temp)
        self.fp.text = str(fan_power * 100) + "%"
        self.wpp.text = str(wp_power * 100) + "%"

        if use_thermometer:
            self.surr_temp.text = str(temp)


if __name__ == '__main__':
    AlbaeApp(name="Albae").run()
