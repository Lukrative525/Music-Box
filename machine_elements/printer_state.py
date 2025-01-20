from enum import Enum
from machine_elements.printer_components import Printer

class Direction(Enum):
    POSITIVE = 1
    NEGATIVE = -1

class PrinterState:
    def __init__(self, printer: Printer):
        self.number_channels = len(printer.axes)
        self.positions = []
        self.directions = []
        self.feedrates = []
        self.time_keeper_position = 0
        for axis in printer.axes:
            self.positions.append(axis.starting_position)
            self.directions.append(Direction.POSITIVE)
            self.feedrates.append(0)

    def reverseDirection(self, channel_number):
        if self.directions[channel_number] == Direction.POSITIVE:
            self.directions[channel_number] = Direction.NEGATIVE
        elif self.directions[channel_number] == Direction.NEGATIVE:
            self.directions[channel_number] = Direction.POSITIVE