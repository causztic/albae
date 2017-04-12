'''
PART 2.1

We decided to use the Proportional-Derivative controller so that we are able to detect sudden temperature changes
in the algae, and increase the fan and water pump's power accordingly.

The function is in the form:
power = k0 * abs(optimal - current) + k1 * [ abs(optimal - current) - abs(optimal - previous) ], and scaled from 0 to 1.

k0 is 1 while k1 is 0.5.
This is to optimize the power consumption based on the current temperature and the project temperature due to rate of change.

If thermometer is detected, use the thermometer. Otherwise, use manual controls.
(We were unable to install the kivy-garden graph library on Pi, use the part2_code_with_gpio instead.)
(This runs perfectly on other systems)
'''


import os
import glob
import time

from functools import partial
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.garden.graph import Graph, MeshLinePlot

from temperature_sm import TemperatureSM
from temperature_widget import TemperatureWidget

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

    def __init__(self, **kwargs):
        App.__init__(self, **kwargs)
        self.temps = []
        self.tsm = TemperatureSM()
        self.fp = Label(text="0.0%", pos_hint={'x': .30, 'center_y': 0.25}, size_hint=(
            None, None), color=(0, 0, 0, 1))
        self.wpp = Label(text="0.0%", pos_hint={'x': .72, 'center_y': 0.25}, size_hint=(
            None, None), color=(0, 0, 0, 1))

        # use a custom temperature widget to reduce code redundancy.
        if use_thermometer:
          self.system_temperature = TemperatureWidget(
              temperature=read_temp(), text="System", pos_hint={'x': .25, 'center_y': .5}, size_hint=(None, None), disable_button=True)
        else:
            self.system_temperature = TemperatureWidget(
              temperature=25.0, text="System (Manual, Thermometer not detected)", pos_hint={'x': .25, 'center_y': .5}, size_hint=(None, None))

        self.target_temperature = TemperatureWidget(
            temperature=27.0, text="Target", pos_hint={'x': .65, 'center_y': .5}, size_hint=(None, None))

    def build(self):
        main = FloatLayout()
        Window.clearcolor = (1, 1, 1, 1)
        main.add_widget(self.target_temperature)
        main.add_widget(self.system_temperature)

        main.add_widget(Label(text="Fan Power",  pos_hint={
                        'x': .22, 'center_y': .25}, size_hint=(None, None), color=(0, 0, 0, 1)))
        main.add_widget(self.fp)
        main.add_widget(Label(text="Water Pump Power",  pos_hint={
                        'x': .6, 'center_y': .25}, size_hint=(None, None),  color=(0, 0, 0, 1)))
        main.add_widget(self.wpp)

        self.graph = Graph(padding=5, x_grid=True, y_grid=True, ymin=20, ymax=35)

        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.graph.add_plot(self.plot)
        main.add_widget(self.graph, 10)

        Clock.schedule_interval(partial(self.updateGUI), 1)
        Clock.schedule_interval(partial(self.update_points), 1)
        Clock.schedule_interval(partial(self.update_xaxis), 1)

        return main

    def update_xaxis(self,*args):
        self.graph.xmin = len(self.temps) - 50
        self.graph.xmax = len(self.temps)

    def update_points(self, *args):
        self.plot.points = [(ind, x) for ind, x in enumerate(self.temps)]


    def updateGUI(self, *largs):
        """ Update GUI based on state machine."""
        self.tsm.optimal = float(self.target_temperature.temperature)
        temp = float(read_temp()) if use_thermometer else float(
            self.system_temperature.temperature)
        
        self.temps.append(temp)
        fan_power, wp_power = self.tsm.step(temp)

        self.fp.text = str(round(fan_power, 2) * 100) + "%"
        self.wpp.text = str(round(wp_power, 2) * 100) + "%"

        self.system_temperature.update_color(self.tsm.state)
        if use_thermometer:
            self.system_temperature.update_temperature(temp)

if __name__ == '__main__':
    AlbaeApp(name="Albae").run()

