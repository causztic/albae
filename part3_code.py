import time
import simpy
import random
from libdw import sm


class TemperatureSM(sm.SM):
    """ Temperature State Machine."""

    startState = "hot"
    k0 = 1
    k1 = 10

    def __init__(self):
        self.state = self.startState
        self._optimal = 27.0
        self.previous_temp = None

    @property
    def optimal(self):
        """ Getter for optimal temperature """
        return self._optimal

    @optimal.setter
    def set_optimal(self, value):
        self._optimal = float(value)

    def getNextValues(self, state, inp):
        """ Get next values in the state machine."""
        scaled = self.k0 * abs(self.optimal - float(inp))

        if self.previous_temp is not None:
            # Scale the value based on a 2nd order equation with error
            # correction
            scaled += self.k1 * \
                (abs(self.optimal - float(inp)) -
                 abs(self.optimal - self.previous_temp))

        self.previous_temp = float(inp)
        power = 1.0
        nextState = "cold"

        # update state based on input
        if float(inp) >= self.optimal:
            nextState = "hot"
        elif float(inp) < self.optimal:
            nextState = "cold"

        # if scaled power is more than 1, set it to 1, which is the maximum.
        if state == "hot":
            if scaled >= 1.0:
                power = 1.0
            elif scaled < 0:
                power = 0.0
            else:
                power = scaled
        # if scaled power is less than 0, set it to 0.
        elif state == "cold":
            if scaled < 0:
                power = 0.0
            else:
                power = 0.0
        return nextState, (power, power)


class AlgaeContainer(object):
    """
    Class to emulate the Algae Container. It runs a process which
    checks it's temperature every second, simulating a thermometer.
    """

    def __init__(self, env):
        self.temperature = simpy.Container(env, init=27.3)
        # monitoring the temperature with a simulated thermometer.
        env.process(self.monitor_temperature(env))

    def monitor_temperature(self, env):
        """Process to monitor the temperature of the algae container."""
        while True:
            # if too low, activate cooling
            if controller.tsm.optimal < self.temperature.level:
                env.process(controller.activate_cooling(env, self))

            # display the time and print the updated temperature.
            m, s = divmod(env.now, 60)
            h, m = divmod(m, 60)

            print "%d:%02d:%02d - Temperature: %.1f" % (h, m, s, self.temperature.level)
            yield env.timeout(1)

class Surroundings(object):
    """
    Class to simulate the surrounding temperature.
    Has a Process which simulates the temperature change due to time of day,
    and a Process to calculate temperature change on the AlgaeContainer based on heat gain from
    the surroundings.
    """

    def __init__(self, env):
        self.temperature = 25.0
        env.process(self.day_night_cycle(env))
        env.process(self.heat_up(env, algae_container))

    def day_night_cycle(self, env):
        """simulate a 24-hour cycle with temperature changes."""
        while True:
            # crude daynight cycle starting from midnight, we wait for 9 hours to morning,
            # raise temperature by 2.5 to 4 degrees
            yield env.timeout(60 * 60 * 9)
            self.temperature += random.uniform(2.5, 4)
            # from 11 to 3, raise temperature by a random number between 4 to 5
            yield env.timeout(60 * 60 * 2)
            self.temperature += random.uniform(4, 5)
            # after 3, decrease temperature by 2.5 to 4 degrees
            yield env.timeout(60 * 60 * 4)
            self.temperature -= random.uniform(2.5, 4)
            # after 7, go back to room temperature
            yield env.timeout(60 * 60 * 4)
            self.temperature = 25.0
            # to midnight and restart again
            yield env.timeout(60 * 60 * 5)

    def heat_up(self, env, algae_container):
        """ Combination of radiation, conduction and convection """
        while True:
            # inverse of thermal resistance of air between the bottle and the
            # surroundings.
            l = 20
            # conduction from the surroundings to the algae_container.
            # this includes convection as well.
            temp_diff = ((1 + l / 2) / (1 - l / 2) * algae_container.temperature.level) - \
                (3 + l * self.temperature) / (1 - l / 2)
            if temp_diff > 0:
                yield algae_container.temperature.put(temp_diff)
            yield env.timeout(1)


class Controller(object):
    """
    Class to simulate the Raspberry Pi controller.
    Uses the state machine to update the water pump power and fan power
    accordingly and updates the AlgaeContainer temperature.
    """
    def __init__(self):
        self.tsm = TemperatureSM()

    def activate_cooling(self, env, algae_container):
        """ Update temperature based on state machine step."""
        fan_power, wp_power = self.tsm.step(
            float(algae_container.temperature.level))
        # over here, generate the temperature decrease with physics
        if wp_power > 0:
            # maximum power = 5
            yield algae_container.temperature.get(1.25 * wp_power)
        else:
            yield env.timeout(1)

# create initial conditions.
rte = simpy.RealtimeEnvironment(factor=0.005)
#rte = simpy.Environment()
algae_container = AlgaeContainer(rte)
surr = Surroundings(rte)
controller = Controller()

rte.run(60 * 60 * 24)  # run for a day
