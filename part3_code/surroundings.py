import random
import simpy
from constants import REDIS_SERVER

class Surroundings(object):
    """
    Class to simulate the surrounding temperature.
    Has a Process which simulates the temperature change due to time of day,
    and a Process to calculate temperature change on the AlgaeContainer based on heat gain from
    the surroundings.
    """

    def __init__(self, env):
        self.env = env
        self.temperature = 25.0
        self.is_night = True
        env.process(self.day_night_cycle(env))
        env.process(self.heat_up(env))

    def day_night_cycle(self, env):
        """simulate a 24-hour cycle with temperature changes."""
        while True:
            # crude daynight cycle starting from midnight, we wait for 9 hours to morning,
            # raise temperature by 2.5 to 4 degrees
            yield env.timeout(60 * 60 * 9)
            self.is_night = False
            self.temperature += random.uniform(2.5, 4)
            # from 11 to 3, raise temperature by a random number between 4 to 5
            yield env.timeout(60 * 60 * 2)
            self.temperature += random.uniform(3, 4)
            # after 3, decrease temperature by 2.5 to 4 degrees
            yield env.timeout(60 * 60 * 4)
            self.temperature -= random.uniform(2.5, 4)
            # after 6, go back to room temperature
            yield env.timeout(60 * 60 * 3)
            self.is_night = True
            self.temperature = 25.0
            # to midnight and restart again
            yield env.timeout(60 * 60 * 6)

    def heat_up(self, env):
        """ Apply convection on the system, and sunlight on the bottle """
        SUNLIGHT = 1.5
        while True:
            l = 0.15
            if self.is_night:
                SUNLIGHT = 0
            temp_diff = l / (167.44 - l / 2) * float(REDIS_SERVER.get("temperature") or 0) + (SUNLIGHT-l*self.temperature) / (167.44-l/2)
            REDIS_SERVER.set("diff", temp_diff)
            print temp_diff
            yield env.timeout(1)


rte = simpy.RealtimeEnvironment(factor=0.1)
surroundings = Surroundings(rte)
rte.run(60 * 60 * 24)  # run for a day
