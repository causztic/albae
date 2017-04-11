import time
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout


class TemperatureWidget(FloatLayout):

    def pretty_temperature(self):
        return str(self.temperature) + u"\u00b0C"

    def __init__(self, **kwargs):
        self.rows = 3
        FloatLayout.__init__(self, **kwargs)

        self.temperature = None
        self.disable_button = False
        self.text = ""

        acceptable_keys_list = ["temperature", "text", "disable_button"]
        for (k, v) in kwargs.iteritems():
            if k in acceptable_keys_list:
                setattr(self, k, v)

        self.widget_text = Label(text=self.text, font_name=(
            "Lato-Bold.ttf"), pos_hint={'x': .25, 'center_y': 1.5}, size_hint=(None, None), color=(0,0,0,1))
        self.temperature_text = Label(
            text=self.pretty_temperature(), font_name=("Lato-Bold.ttf"), pos_hint={'x': .25, 'center_y': 0}, size_hint=(None, None), color=(0,0,0,1))
        self.increment_temp_btn = Button(on_press=self.plus_temp, text="+", font_name=(
            "Lato-Bold.ttf"), pos_hint={'x': -0.5, 'center_y': -1.5}, size_hint=(None, None))
        self.decrement_temp_btn = Button(on_press=self.minus_temp, text="-", font_name=(
            "Lato-Bold.ttf"), pos_hint={'x': 0.95, 'center_y': -1.5}, size_hint=(None, None))

        self.add_widget(self.widget_text)
        self.add_widget(self.temperature_text)
        self.temperature = float(self.temperature)
        if not self.disable_button:
            self.add_widget(self.increment_temp_btn)
            self.add_widget(self.decrement_temp_btn)

    def plus_temp(self, instance):
        """increase target temperature by 0.1"""
        self.temperature += 0.1
        self.temperature_text.text = self.pretty_temperature()

    def minus_temp(self, instance):
        """decrease target temperature by 0.1"""
        self.temperature -= 0.1
        self.temperature_text.text = self.pretty_temperature()

    def update_temperature(self, temp):
        self.temperature = float(temp)
        self.temperature_text.text = str(temp)

    def update_color(self, state):
        if state == "hot":
            self.temperature_text.color = 1,0,0,1
        else:
            self.temperature_text.color = 0,0,1,1