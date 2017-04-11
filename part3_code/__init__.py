"""
    SIMULATOR!
    Run this file to simulate the Water Pump, Fan, and the AlgaeContainer.
    
    Run controller.py to simulate the thermometer on the Pi to output power based on the temperature 
    to the Water Pump and Fan.

    Run surroundings.py to introduce convection of the surroundings on to the AlgaeContainer.

"""
import time
import simpy
import random
from constants import REDIS_SERVER

class WaterPump(object):
    def __init__(self, env):
        self.env = env
        self.power = 0.0
        env.process(self.pump_water(env))

    def pump_water(self, env):
        while True: 
            self.power = float(REDIS_SERVER.get("wp_power") or 0)
            # the power will affect the rate of water pump and hence affecting the temperature.
            REDIS_SERVER.set("diff", ((-4*self.power)/(167.44+2*self.power)) * float(REDIS_SERVER.get("temperature") or 0) + ((6+4*25)*self.power) / (2*self.power + 167.44))
            REDIS_SERVER.set("wp_power", 0)
            yield env.timeout(1)

class Fan(object):
    def __init__(self, env):
        self.env = env
        self.power = 0.0
        env.process(self.blow_air(env))

    def blow_air(self, env):
        while True:
            self.power = float(REDIS_SERVER.get("fan_power") or 0)
            REDIS_SERVER.set("fan_power", 0)
            yield env.timeout(1)


class AlgaeContainer(object):
    """
    Class to emulate the Algae Container. It runs a process which
    checks it's temperature every second, simulating a thermometer.
    """

    def __init__(self, env):
        self.env = env
        self.temperature = simpy.Container(env, init=30)
        # monitoring the temperature with a simulated thermometer.
        env.process(self.monitor_temperature(env))

    def monitor_temperature(self, env):
        """Process to monitor the temperature of the algae container."""
        while True:
            # display the time and print the updated temperature.
            m, s = divmod(env.now, 60)
            h, m = divmod(m, 60)
            print "%d:%02d:%02d - Temperature: %.2f" % (h, m, s, self.temperature.level)
            diff = REDIS_SERVER.get("diff")
            if diff is not None:
                diff = float(diff)
                if diff > 0:
                    self.temperature.put(diff)
                elif diff < 0:
                    self.temperature.get(abs(diff))
            REDIS_SERVER.set("diff", 0)
            REDIS_SERVER.set("temperature", self.temperature.level)

            yield env.timeout(1)
# clear redis-server
REDIS_SERVER.delete("diff", "temperature", "wp_power", "fan_power")
# create initial conditions.
rte = simpy.RealtimeEnvironment(factor=0.1)
algae_container = AlgaeContainer(rte)
water_pump = WaterPump(rte)
fan = Fan(rte)

rte.run(60 * 60 * 24)  # run for a day

"""
Your task is define and implement Processes that increase and decrease the temperature of the system.

# Discuss what are the processes that increase the temperature.
- The Processes that increase the temperature are done by the Surrounding on the AlgaeContainer.
- These include the ambient temperature difference during night and day, and temperature
- gain due to conduction, convection and radiation.

# Discuss what are the processes that decrease the temperature.
- The processes that decrease the temperature would be the water pump activated by the Controller
  on the AlgaeContainer, and the fan.
- When it's night time the temperature will also decrease.

# Discuss what are the shared resources in those processes.
- Temperature is the shared resource here.

# Discuss how to implement those processes and shared resources using Simpy.
"""