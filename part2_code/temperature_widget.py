from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

class TemperatureWidget(BoxLayout):

    def __init__(self, **kwargs):
        BoxLayout.__init__(self, **kwargs)
        acceptable_keys_list = ["sm", "temperature"]
        for k in kwargs.keys():
            if k in acceptable_keys_list:
                self.__setattr__(k, kwargs[k])

        self.temperature = float(self.temperature)
        self.temperature_text = Label(text=str(self.temperature))
        self.increment_temp_btn = Button(on_press=self.plus_temp, text="+")
        self.decrement_temp_btn = Button(
            on_press=self.minus_temp, text="-")

        self.add_widget(self.temperature_text)
        self.add_widget(self.increment_temp_btn)
        self.add_widget(self.decrement_temp_btn)

    def plus_temp(self, instance):
        """increase target temperature by 0.1"""
        self.temperature += 0.1
        self.temperature_text.text = str(self.temperature)
        
    def minus_temp(self, instance):
        """decrease target temperature by 0.1"""
        self.temperature -= 0.1
        self.temperature_text.text = str(self.temperature)
