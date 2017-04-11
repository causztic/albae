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