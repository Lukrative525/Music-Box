from enum import Enum

class Axis:
    class AxisType(Enum):
        LINEAR = "linear"
        ROTARY = "rotary"

    def __init__(self,
            label: str,
            axis_type: AxisType=None,
            upper_limit=None,
            lower_limit=None,
            max_feed_rate=None,
            starting_position=None,
            base_steps_per_millimeter=None,
            microstepping_factor=None):

        self.label = label

        self.axis_type = axis_type
        self.limits = AxisLimits(upper_limit, lower_limit)
        self.max_feed_rate = max_feed_rate
        self.starting_position = starting_position

        self._base_steps_per_millimeter = None
        self._microstepping_factor = None

        self.base_steps_per_millimeter = base_steps_per_millimeter
        self.microstepping_factor = microstepping_factor

    @property
    def base_steps_per_millimeter(self):
        return self._base_steps_per_millimeter

    @base_steps_per_millimeter.setter
    def base_steps_per_millimeter(self, base_steps_per_millimeter):
        self._base_steps_per_millimeter = base_steps_per_millimeter
        if self._microstepping_factor is not None:
            self._steps_per_millimeter = self._base_steps_per_millimeter * self._microstepping_factor

    @property
    def microstepping_factor(self):
        return self._microstepping_factor

    @microstepping_factor.setter
    def microstepping_factor(self, microstepping_factor):
        self._microstepping_factor = microstepping_factor
        if self._base_steps_per_millimeter is not None:
            self._steps_per_millimeter = self._base_steps_per_millimeter * self._microstepping_factor

    @property
    def steps_per_millimeter(self):
        return self._steps_per_millimeter

    def isComplete(self):
        if self.axis_type is None:
            return False
        elif self.limits is None:
            return False
        elif self.max_feed_rate is None:
            return False
        elif self.starting_position is None:
            return False
        elif self.base_steps_per_millimeter is None:
            return False
        elif self.microstepping_factor is None:
            return False
        elif self.steps_per_millimeter is None:
            return False
        return True

class AxisLimits:
    def __init__(self, upper, lower):
        if upper <= lower:
            raise Exception("Axis limits error: upper limit must be greater than lower limit")
        self.upper = upper
        self.lower = lower

    def isWithinLimits(self, value):
        if value <= self.upper and value >= self.lower:
            return True
        return False

class TimeKeeper:
    def __init__(self, label: str, feed_rate):
        self.label = label
        self.feed_rate = feed_rate

class Printer:
    Axis = Axis

    def __init__(self):
        self.axes: list[Axis] = []
        self.time_keeper: TimeKeeper = None

    def addAxis(self, label: str, axis_type: Axis.AxisType, upper_limit, lower_limit, max_feed_rate, starting_position, base_steps_per_millimeter, microstepping_factor):
        new_axis = Axis(label, axis_type, upper_limit, lower_limit, max_feed_rate, starting_position, base_steps_per_millimeter, microstepping_factor)
        self.axes.append(new_axis)

    def isComplete(self):
        if len(self.axes) < 1:
            return False
        for axis in self.axes:
            if not axis.isComplete():
                return False
        if self.time_keeper is None:
            return False
        return True

    def setTimeKeeper(self, label, feed_rate):
        self.time_keeper = TimeKeeper(label, feed_rate)