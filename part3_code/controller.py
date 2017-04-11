from temperature_sm import TemperatureSM
import simpy
from constants import REDIS_SERVER

class Controller(object):
    """
    Class to simulate the Raspberry Pi controller.
    Uses the state machine to update the water pump power and fan power
    accordingly and updates the AlgaeContainer temperature.
    """
    def __init__(self, env):
        self.env = env
        self.power_consumption = 0
        self.tsm = TemperatureSM()
        env.process(self.activate_cooling(env))

    def activate_cooling(self, env):
        """ Update temperature based on state machine step."""
        while True:
            fan_power, wp_power = self.tsm.step(float(REDIS_SERVER.get("temperature")))
            REDIS_SERVER.set("wp_power", wp_power)
            REDIS_SERVER.set("fan_power", fan_power)
            print fan_power, wp_power
            if wp_power > 0:
                # maximum power = 5
                # we use the power % to calculate the mass flow rate and hence decreasing the temperature
                self.power_consumption += wp_power * 5
            if fan_power > 0:
                self.power_consumption += fan_power * 5

            yield env.timeout(1)

rte = simpy.RealtimeEnvironment(factor=0.1)
controller = Controller(rte)
rte.run(60 * 60 * 24)  # run for a day
print controller.power_consumption * 7
