from enum import Enum
from machine_elements.printer_components import Printer

class Direction(Enum):
    POSITIVE = 1
    NEGATIVE = -1

class PrinterState:
    def __init__(self, printer: Printer):
        self.number_channels = len(printer.axes)
        self.printer = printer
        self.positions = [0] * self.number_channels
        self.directions = [Direction.POSITIVE] * self.number_channels
        self.feedrates = [0] * self.number_channels
        self.time_keeper_position = 0

        self.resetState()

    def resetState(self):
        for index, axis in enumerate(self.printer.axes):
            self.positions[index] = axis.starting_position
            self.directions[index] = Direction.NEGATIVE
            self.feedrates[index] = 0
        self.time_keeper_position = 0

    def reverseDirection(self, channel_index):
        if self.directions[channel_index] == Direction.POSITIVE:
            self.directions[channel_index] = Direction.NEGATIVE
        elif self.directions[channel_index] == Direction.NEGATIVE:
            self.directions[channel_index] = Direction.POSITIVE