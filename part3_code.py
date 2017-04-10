import time
import simpy
import random
from libdw import sm


class TemperatureSM(sm.SM):

    startState = "hot"
    k0 = 1
    k1 = 10

    def __init__(self):
        self.state = self.startState
        self._optimal = 27.0
        self.previous_temp = None

    @property
    def optimal(self):
        return self._optimal

    @optimal.setter
    def set_optimal(self, value):
        self._optimal = float(value)

    def getNextValues(self, state, inp):
        scaled = self.k0 * abs(self.optimal - float(inp))

        if self.previous_temp is not None:
            scaled += self.k1 * (abs(self.optimal - float(inp)) - abs(self.optimal - self.previous_temp))

        self.previous_temp = float(inp)
        power = 1.0
        nextState = "cold"

        if float(inp) >= self.optimal:
            nextState = "hot"
        elif float(inp) < self.optimal:
            nextState = "cold"

        if state == "hot":
            if scaled >= 1.0:
                power = 1.0
            elif scaled < 0:
                power = 0.0
            else:
                power = scaled
        elif state == "cold":
            if scaled < 0:
                power = 0.0
            else:
                power = 0.0
        return nextState, (power, power)

class AlgaeContainer(object):

    def __init__(self, env):
        self.temperature = simpy.Container(env, init=27.3)
        # monitoring the temperature with a simulated thermometer.
        env.process(self.monitor_temperature(env))


    def monitor_temperature(self, env):
        while True:
            # if too low, activate cooling
            if controller.tsm.optimal < self.temperature.level:
                env.process(controller.activate_cooling(env, self))
            m, s = divmod(env.now, 60)
            h, m = divmod(m, 60)

            print "%d:%02d:%02d - Temperature: %.1f" % (h, m, s, self.temperature.level)
            yield env.timeout(1)

class Surroundings(object):
    def __init__(self, env):
        self.temperature = 25.0
        env.process(self.day_night_cycle(env))
        env.process(self.conduction(env, algae_container))

    def day_night_cycle(self, env):
        while True:
            # crude daynight cycle starting from midnight, we wait for 9 hours to morning, 
            # raise temperature by 2.5 to 4 degrees
            yield env.timeout(60*60*9)
            self.temperature += random.uniform(2.5, 4)
            # from 11 to 3, raise temperature by a random number between 4 to 5
            yield env.timeout(60*60*2)
            self.temperature += random.uniform(4, 5)
            # after 3, decrease temperature by 2.5 to 4 degrees
            yield env.timeout(60*60*4)
            self.temperature -= random.uniform(2.5, 4)
            # after 7, go back to room temperature
            yield env.timeout(60*60*4)
            self.temperature = 25.0
            # to midnight and restart again
            yield env.timeout(60*60*5)

    def conduction(self, env, algae_container):
        while True:
            l = 20 #inverse of thermal resistance of air between the bottle and the surroundings.
            #conduction from the surroundings to the algae_container.
            #this includes convection as well.
            temp_diff = ((1 + l/2)/(1- l/2)*algae_container.temperature.level) - (3+l*self.temperature)/(1-l/2)
            if temp_diff > 0:
                yield algae_container.temperature.put(temp_diff)
            yield env.timeout(1)

class Controller(object):
    def __init__(self):
        self.tsm = TemperatureSM()

    def activate_cooling(self, env, algae_container):
        fan_power, wp_power = self.tsm.step(float(algae_container.temperature.level))
        # over here, generate the temperature decrease with physics
        if wp_power > 0:
            # maximum power = 5
            yield algae_container.temperature.get(1.25*wp_power)
        else:
            yield env.timeout(1)

# refactored controller to consist of the fan, water pump,
# and the state_machine needed to control those
# items based on the simulated algae_container.

#env = simpy.RealtimeEnvironment(factor=0.005)
env = simpy.Environment()

algae_container = AlgaeContainer(env)
surr = Surroundings(env)
controller = Controller()

env.run(60*60*24) # run for a day