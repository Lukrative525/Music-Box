from midi_elements import *
from machine_elements.printer_components import Printer, Axis, AxisType, isWithinLimits
from machine_elements.printer_state import PrinterState
from math import sqrt
from note_buffer import NoteBuffer
from typing import TextIO

class PrinterGcodeGenerator:
    def __init__(self, machine: Printer):
        self.machine: Printer = machine
        self.machine_state: PrinterState = PrinterState(self.machine)

    def checkTrackCompatibility(self, track: Track):
        if len(track.channels) > len(self.machine.axes):
            raise Exception("Number of channels exceeds number of available axes. Remove channels or add more axes.")
        if max(track.channels) > len(self.machine.axes) - 1:
            raise Exception("The highest channel index in the input midi file is higher than the highest available machine axis index.")
        if not track.hasTimeEventsAllOfType(TimeEventType.DELTA):
            raise Exception(f"Track time events must all be of type \"{TimeEventType.DELTA.value}\".")

    def determineDirections(self, current_note_buffer: NoteBuffer, previous_note_buffer: NoteBuffer):
        for channel_index in current_note_buffer.channel_indices:
            if not current_note_buffer.channels[channel_index].isEmpty() and previous_note_buffer.channels[channel_index].isEmpty():
                self.machine_state.reverseDirection(channel_index)

    def determineFeedRates(self, current_note_buffer: NoteBuffer):
        for channel_index in current_note_buffer.channel_indices:
            if current_note_buffer.channels[channel_index].isEmpty():
                self.machine_state.feedrates[channel_index] = 0
            else:
                note_number = current_note_buffer.channels[channel_index].getNote()
                self.machine_state.feedrates[channel_index] = round(calculateFeedRate(note_number, self.machine.axes[channel_index]), self.machine.precision)

    def determinePositions(self, current_note_buffer: NoteBuffer):
        for channel_index in current_note_buffer.channel_indices:
            travel_amount = self.machine_state.feedrates[channel_index] * current_note_buffer.duration / 60
            new_position = self.machine_state.positions[channel_index] + self.machine_state.directions[channel_index].value * travel_amount
            if isWithinLimits(new_position, self.machine.axes[channel_index]):
                self.machine_state.positions[channel_index] = round(new_position, self.machine.precision)
            else:
                self.machine_state.reverseDirection(channel_index)
                new_position = self.machine_state.positions[channel_index] + self.machine_state.directions[channel_index].value * travel_amount
                if isWithinLimits(new_position, self.machine.axes[channel_index]):
                    self.machine_state.positions[channel_index] = round(new_position, self.machine.precision)
                else:
                    raise Exception("Requested travel amount exceeds the available axis travel amount.")

        self.machine_state.time_keeper_position = round(self.machine.time_keeper.feed_rate * current_note_buffer.duration / 60, self.machine.precision)

    def generatePrinterGcode(self, target_file, track: Track):

        """
        For generating musical gcode to run on FDM 3D printers
        target_file is a string containing the file you want to write the gcode to.
        """

        self.checkTrackCompatibility(track)

        self.machine_state.resetState()

        file_stream = open(target_file, "w")
        self.writeStartGcode(file_stream)

        current_note_buffer = NoteBuffer(track.channels)
        previous_note_buffer = NoteBuffer(track.channels)
        for event in track:
            if isinstance(event, NoteOnEvent):
                current_note_buffer.channels[event.channel_index].add(event.note_number)
            elif isinstance(event, NoteOffEvent):
                current_note_buffer.channels[event.channel_index].remove(event.note_number)
            elif isinstance(event, TimeEvent) and event.value > 0:
                current_note_buffer.duration = event.value
                self.determineDirections(current_note_buffer, previous_note_buffer)
                self.determineFeedRates(current_note_buffer)
                self.determinePositions(current_note_buffer)
                self.writeMovementCommand(file_stream)
                previous_note_buffer.copyNotes(current_note_buffer)

        self.writeEndGcode(file_stream)
        file_stream.close()

    def writeEndGcode(self, file_stream: TextIO):
        file_stream.write("M302 P0; disallow cold extrusion\n")
        file_stream.write("G4 S1; pause for a second\n")

    def writeMovementCommand(self, file_stream: TextIO):
        total_feedrate = 0
        for channel_index, feedrate in enumerate(self.machine_state.feedrates):
            total_feedrate += feedrate ** 2
        total_feedrate = round(sqrt(total_feedrate), self.machine.precision)
        if total_feedrate == 0:
            total_feedrate = abs(self.machine.time_keeper.feed_rate)

        movement_command = f"G1 F{total_feedrate}"
        for channel_index, axis in enumerate(self.machine.axes):
            if not self.machine_state.feedrates[channel_index] == 0:
                movement_command += f" {axis.label}{self.machine_state.positions[channel_index]}"
        movement_command += f" {self.machine.time_keeper.label}{self.machine_state.time_keeper_position}\n"

        file_stream.write(movement_command)

    def writeStartGcode(self, file_stream: TextIO):
        file_stream.write("M302 P1; allow cold extrusion\n")
        file_stream.write("M83; relative extruder moves\n")

        file_stream.write(f"G92 {self.machine.time_keeper.label}0; reset {self.machine.time_keeper.label} axis\n")
        linear_axes_command = "G1 F60000000"
        rotary_axes_command = "G92"
        linear_axes_present = False
        rotary_axes_present = False
        for axis in self.machine.axes:
            if axis.axis_type == AxisType.LINEAR:
                linear_axes_present = True
                linear_axes_command += f" {axis.label}{axis.starting_position}"
            elif axis.axis_type == AxisType.ROTARY:
                rotary_axes_present = True
                rotary_axes_command += f" {axis.label}{axis.starting_position}"
        if linear_axes_present:
            linear_axes_command += "; center axis/axes\n"
            file_stream.write(linear_axes_command)
        if rotary_axes_present:
            rotary_axes_command += "; reset axis/axes\n"
            file_stream.write(rotary_axes_command)

        file_stream.write("G4 S1; pause for a second\n")

def calculateFeedRate(note_number: int, axis: Axis):

    """
    For calculating feedrate in mm/min
    """

    frequency = calculateFrequency(note_number)
    feed_rate = frequency * 60 / axis.steps_per_millimeter

    return feed_rate

def calculateFrequency(note_number):

    """
    For calculating frequencies of notes (in hertz) based on A440, note number 69
    """

    frequency = 440 * (2 ** ((note_number - 69) / 12))

    return frequency