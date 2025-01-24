from midi_elements import *
from machine_elements.printer_components import Printer, Axis, AxisType
from machine_elements.printer_state import PrinterState, Direction
from math import floor, sqrt
from note_buffer import NoteBuffer
from typing import TextIO

note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

class PrinterGcodeGenerator:
    def __init__(self, machine: Printer):
        self.machine = machine
        self.machine_state = PrinterState(self.machine)

    def checkTrackCompatibility(self, track: Track):
        if len(track.channels) > len(self.machine.axes):
            raise Exception("Number of channels exceeds number of available axes. Remove channels or add more axes.")
        if max(track.channels) > len(self.machine.axes) - 1:
            raise Exception("The highest channel number in the input midi file exceeds the number of available axes. Each channel added in the midi file should use the lowest channel number available.")
        if not track.hasTimeEventsAllOfType(TimeEventType.DELTA):
            raise Exception(f"Track time events must all be of type \"{TimeEventType.DELTA.value}\"")

    def flipDirection(self, channel_number):
        if self.machine_state.directions[channel_number] == Direction.POSITIVE:
            self.machine_state.directions[channel_number] = Direction.NEGATIVE
        elif self.machine_state.directions[channel_number] == Direction.NEGATIVE:
            self.machine_state.directions[channel_number] = Direction.POSITIVE

    def generatePrinterGcode(self, target_file, track: Track):

        """
        For generating musical gcode to run on FDM 3D printers
        target_file is a string containing the file you want to write the gcode to.
        """

        self.checkTrackCompatibility(track)

        file_stream = open(target_file, "w")
        self.writeStartGcode(file_stream)

        current_notes = NoteBuffer(len(track.channels))
        previous_notes = NoteBuffer(len(track.channels))
        for event in track:
            if isinstance(event, NoteOnEvent):
                current_notes.channels[event.channel_number].add(event.note_number)
            elif isinstance(event, NoteOffEvent):
                current_notes.channels[event.channel_number].remove(event.note_number)
            elif isinstance(event, TimeEvent):
                current_notes.duration = event.value
                self.updateMachineState(current_notes, previous_notes)
                self.writeMovementCommand(file_stream)
                previous_notes.copyNotes(current_notes)

        self.writeEndGcode(file_stream)
        file_stream.close()

    def updateMachineState(self, current_notes: NoteBuffer, previous_notes: NoteBuffer):
        for channel_number in range(self.machine_state.number_channels):
            if not current_notes.channels[channel_number] == previous_notes.channels[channel_number]:
                print("Notes changed!")

    def writeEndGcode(self, file_stream: TextIO):
        file_stream.write("M302 P0; disallow cold extrusion\n")
        file_stream.write("G4 S1; pause for a second\n")

    def writeMovementCommand(self, file_stream: TextIO):
        total_feedrate = 0
        for channel_number in range(len(self.machine.axes)):
            total_feedrate += self.machine_state.feedrates[channel_number] ** 2
        total_feedrate = sqrt(total_feedrate)
        if total_feedrate == 0:
            total_feedrate = abs(self.machine.time_keeper.feed_rate)

        movement_command = f"G1 F{total_feedrate}"
        for channel_number, axis in enumerate(self.machine.axes):
            if not self.machine_state.feedrates[channel_number] == 0:
                movement_command += f" {axis.label}{self.machine_state.positions[channel_number]}"
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

def convertMidiToPitchNotation(note_number):

    """
    For converting midi note numbers (e.g. 69) to scientific pitch notation (e.g. A4)
    """

    octave = int(floor(note_number / 12) - 1)
    note = note_names[note_number % 12]

    return note + str(octave)
