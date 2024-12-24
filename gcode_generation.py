from midi_elements import *
from machine_components.printer_components import Printer, Axis
from math import floor, sqrt
from note_buffer import NoteBuffer
from typing import TextIO

note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# class MovementComponent:
#     def __init__(self, label: str, feedrate=0, position=None):
#         self.label = label
#         self.feedrate = feedrate
#         self.position = position

# class LinearMovement:
#     def __init__(self, time_keeper: MovementComponent=None):
#         self.components: dict[int, MovementComponent] = {}
#         self.time_keeper = time_keeper

#     def addMovementComponent(self, index, new_movement_component: MovementComponent):
#         self.components[index] = new_movement_component

#     def generateMovementCommand(self, comment: str=None):
#         command_string = f"G1 F{self.calculateTotalFeedrate()}"
#         for index, component in sorted(self.components.items()):
#             if component.position is None:
#                 raise Exception("Cannot generate movement command when position has not been defined")
#             command_string += f" {component.label}{round(component.position, 5)}"
#         if self.time_keeper is not None:
#             command_string += f" {self.time_keeper.label}{round(self.time_keeper.position, 5)}"
#         if comment is not None:
#             command_string += f"; {comment}"
#         command_string += "\n"

#         return command_string

#     def calculateTotalFeedrate(self):
#         feedrate_squared = 0
#         for component in self.components.values():
#             feedrate_squared += component.feedrate ** 2

#         if feedrate_squared == 0 and self.time_keeper is not None:
#             feedrate = abs(self.time_keeper.feedrate)
#         else:
#             feedrate = sqrt(feedrate_squared)

#         return round(feedrate, 5)

#     def clear(self):
#         self.components.clear()

#     def removeMovementComponent(self, index):
#         if index in self.components:
#             del self.components[index]

def calculateFeedRate(note_number, axis: Axis):

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

def checkCompatibility(track: Track, machine: Printer):

    if len(track.channels) > len(machine.axes):
        raise Exception("Number of channels exceeds number of available axes. Remove channels or add more axes.")
    if max(track.channels) > len(machine.axes) - 1:
        raise Exception("The highest channel number in the input midi file exceeds the number of available axes. Each channel added in the midi file should use the lowest channel number available.")
    if not track.hasTimeEventsAllOfType(TimeEventType.DELTA):
        raise Exception(f"Track time events must all be of type \"{TimeEventType.DELTA.value}\"")

def convertMidiToPitchNotation(note_number):

    """
    For converting midi note numbers (e.g. 69) to scientific pitch notation (e.g. A4)
    """

    octave = int(floor(note_number / 12) - 1)
    note = note_names[note_number % 12]

    return note + str(octave)

def generatePrinterGcode(target_file, track: Track, machine: Printer):

    """
    For generating musical gcode to run on FDM 3D printers
    target_file is a string containing the file you want to write the gcode to.
    """

    checkCompatibility(track, machine)

    file_stream = open(target_file, "w")
    writeStartGcode(file_stream, machine)

    note_buffer = NoteBuffer(len(track.channels))
    for event in track:
        if isinstance(event, NoteOnEvent):
            note_buffer.channels[event.channel_number].add(event.note_number)
        elif isinstance(event, NoteOffEvent):
            note_buffer.channels[event.channel_number].remove(event.note_number)
        elif isinstance(event, TimeEvent):
            note_buffer.duration = event.value / 1e6 / 60
            writeMovementCommand(file_stream, note_buffer, machine)

    writeEndGcode(file_stream)
    file_stream.close()

def writeEndGcode(file_stream: TextIO):
    file_stream.write("M302 P0; disallow cold extrusion\n")
    file_stream.write("G4 S1; pause for a second\n")

def writeMovementCommand(file_stream: TextIO, note_buffer: NoteBuffer, machine: Printer):

    command_string = "G1"
    for channel_number in range(len(machine.axes)):
        if len(note_buffer.channels[channel_number]) != 1:
            return
        note_number = min(note_buffer.channels[channel_number])
        feedrate = calculateFeedRate(note_number, machine.axes[channel_number])

def writeStartGcode(file_stream: TextIO, machine: Printer):
    file_stream.write("M302 P1; allow cold extrusion\n")
    file_stream.write("M83; relative extruder moves\n")

    # centering_command = LinearMovement()
    # file_stream.write(f"G92 {machine.time_keeper.label}0; reset {machine.time_keeper.label} axis/axes\n")
    # for index, axis in enumerate(machine.axes):
    #     if axis.axis_type == AxisType.ROTARY:
    #         file_stream.write(f"G92 {axis.label}{axis.starting_position}; reset {axis.label} axis/axes\n")
    #     elif axis.axis_type == AxisType.LINEAR:
    #         centering_command.addMovementComponent(index, MovementComponent(axis.label, axis.max_feed_rate, axis.starting_position))
    # file_stream.write(centering_command.generateMovementCommand("center axis/axes"))

    file_stream.write("G4 S1; pause for a second\n")
