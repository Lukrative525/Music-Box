import numpy as np
from midi_elements import *
from machine_components.printer_components import Printer

note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def calculateFeedRate(note: NoteOnEvent, machine: Printer):

    frequency = calculateFrequency(note.note_number)
    feed_rate = frequency * 60 / machine.axes[note.channel_number].steps_per_millimeter

    return feed_rate

def calculateFrequency(note_number):

    '''
    For calculating frequencies of notes
    '''

    # this formula calculates the frequency of our key number based on A440, key number 69
    frequency = 440 * (2 ** ((note_number - 69) / 12))

    return frequency

def checkCompatibility(track: Track, machine: Printer):

    if len(track.channels) > len(machine.axes):
        raise Exception("Number of channels exceeds number of available axes. Remove channels or add more axes.")
    if max(track.channels) > len(machine.axes) - 1:
        raise Exception("The highest channel number in the input midi file exceeds the number of available axes. Each channel added in the midi file should use the lowest channel number available.")

def convertMidiToPitchNotation(note_number):

    '''
    For converting midi note numbers (e.g. 69) to scientific pitch notation (e.g. A4)
    '''

    octave = int(np.floor(note_number / 12) - 1)
    note = note_names[note_number % 12]

    return note + str(octave)

def generatePrinterGcode(target_file, track: Track, machine: Printer):

    '''
    For generating musical gcode to run on FDM 3D printers
    target_file is a string containing the file you want to write the gcode to.
    '''

    checkCompatibility(track, machine)

    output = open(target_file, "w")
    output.write(f"M302 P1; allow cold extrusion\n")
    output.write("M83; relative extruder moves\n")

    output.write(f"M302 P0; disallow cold extrusion\n")
    output.write("G4 S1; pause for a second")
    output.close()

if __name__ == "__main__":
    from machines import printer_of_theseus
    test_note = NoteOnEvent(1, 59, 80)
    print(printer_of_theseus.axes[1].steps_per_millimeter)
    print(calculateFeedRate(test_note, printer_of_theseus))