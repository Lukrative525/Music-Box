from enum import Enum

class Axis:
    class AxisType(Enum):
        LINEAR = "linear"
        ROTARY = "rotary"

    def __init__(self, label: str):
        self.label = label

        self.axis_type: Axis.AxisType = None
        self.limits: AxisLimits = None
        self.max_feed_rate = None
        self.starting_position = None

        self._base_steps_per_millimeter = None
        self._microstepping_factor = None
        self._steps_per_millimeter = None

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
        self.axes = []
        self.time_keeper = None

    def addAxis(self, label, axis_type, upper_limit, lower_limit, max_feed_rate, starting_position, base_steps_per_millimeter, microstepping_factor):
        new_axis = Axis(label)
        new_axis.axis_type = axis_type
        axis_limits = AxisLimits(upper_limit, lower_limit)
        new_axis.limits = axis_limits
        new_axis.max_feed_rate = max_feed_rate
        new_axis.starting_position = starting_position
        new_axis.base_steps_per_millimeter = base_steps_per_millimeter
        new_axis.microstepping_factor = microstepping_factor
        self.axes.append(new_axis)

    def setTimeKeeper(self, label, feed_rate):
        self.time_keeper = TimeKeeper(label, feed_rate)