import numpy as np
from enum import Enum, auto
from binary_tools import *
from midi_elements import *

class RunningStatus(Enum):
    CONTROL_CHANGE = auto()
    NONE = auto()
    NOTE_OFF = auto()
    NOTE_ON = auto()
    PROGRAM_CHANGE = auto()

def extractVariableLengthQuantity(byte_data, index):

    is_looking_for_end = True
    vlq_bits = ""
    vlq_length = 1

    while is_looking_for_end:
        current_bits = getBits(byte_data[index])
        vlq_bits += current_bits[1:]
        if current_bits[0] == "1":
            index += 1
            vlq_length += 1
        else:
            is_looking_for_end = False

    vlq_value = convertBitStringToUnsignedInt(vlq_bits)

    return [vlq_value, vlq_length]

def getDeltaTime(byte_data, index):

    delta_time, delta_time_byte_length = extractVariableLengthQuantity(byte_data, index)

    return [delta_time, delta_time_byte_length]

def getTrackName(byte_data, index):

    vlq_value, vlq_length = extractVariableLengthQuantity(byte_data, (index + 2))
    chunk_length = vlq_value

    name = ""
    for k in range(chunk_length):
        byte_value = byte_data[index + 2 + vlq_length + k]
        if byte_value != 0:
            name += chr(byte_value)
    name_byte_length = 2 + vlq_length + chunk_length

    return [name, name_byte_length]

# Header Functions

def isMidiFile(byte_data):

    if byte_data[0] == ord("M") and byte_data[1] == ord("T") and byte_data[2] == ord("h") and byte_data[3] == ord("d"):
        return True
    else:
        return False

def getNumberOfTracks(byte_data):

    format_type = byte_data[9]
    if format_type == 0:
        tracks = 1
    elif format_type == 1 or format_type == 2:
        tracks = concatenateBytes(byte_data[10:12])

    return tracks

def getTicksPerBeat(byte_data):

    bits = getBits(byte_data[12])
    if bits[0] == "0":
        ticks_per_beat = concatenateBytes(byte_data[12:14])
        return ticks_per_beat
    else:
        raise Exception("I don\'t know how to handle this time format")

def isTrackStart(byte_data, index):

    if byte_data[index] == ord("M") and byte_data[index + 1] == ord("T") and byte_data[index + 2] == ord("r") and byte_data[index + 3] == ord("k"):
        return True
    else:
        return False

# Meta Event Functions

def isMetaEvent(byte_data, index):

    if hex(byte_data[index]) == "0xff":
        return True
    else:
        return False

def isTrackName(byte_data, index):

    if hex(byte_data[index]) == "0xff" and hex(byte_data[index + 1]) == "0x3":
        return True
    else:
        return False

def isMidiPort(byte_data, index):

    if hex(byte_data[index]) == "0xff" and hex(byte_data[index + 1]) == "0x21" and hex(byte_data[index + 2]) == "0x1":
        return True
    else:
        return False

def isTrackEnd(byte_data, index):

    if hex(byte_data[index]) == "0xff" and hex(byte_data[index + 1]) == "0x2f" and hex(byte_data[index + 2]) == "0x0":
        return True
    else:
        return False

def isTempoChange(byte_data, index):

    if hex(byte_data[index]) == "0xff" and hex(byte_data[index + 1]) == "0x51" and hex(byte_data[index + 2]) == "0x3":
        return True
    else:
        return False

def isTimeSignature(byte_data, index):

    if hex(byte_data[index]) == "0xff" and hex(byte_data[index + 1]) == "0x58" and hex(byte_data[index + 2]) == "0x4":
        return True
    else:
        return False

def isKeySignature(byte_data, index):

    if hex(byte_data[index]) == "0xff" and hex(byte_data[index + 1]) == "0x59" and hex(byte_data[index + 2]) == "0x2":
        return True
    else:
        return False

# Channel-Specific

def isNoteOff(byte_data, index):

    bits = getBits(byte_data[index])

    if bits[0:4] == "1000":
        return True
    else:
        return False

def isNoteOn(byte_data, index):

    bits = getBits(byte_data[index])

    if bits[0:4] == "1001":
        return True
    else:
        return False

def isControlChange(byte_data, index):

    bits = getBits(byte_data[index])

    if bits[0:4] == "1011":
        return True
    else:
        return False

def isProgramChange(byte_data, index):

    bits = getBits(byte_data[index])

    if bits[0:4] == "1100":
        return True
    else:
        return False

# Channel-Agnostic

def isPan(byte_data, index):

    if hex(byte_data[index]) == "0xa":
        return True
    else:
        return False

def isReverb(byte_data, index):

    if hex(byte_data[index]) == "0x5b":
        return True
    else:
        return False

def isTremolo(byte_data, index):

    if hex(byte_data[index]) == "0x5c":
        return True
    else:
        return False

def isChorus(byte_data, index):

    if hex(byte_data[index]) == "0x5d":
        return True
    else:
        return False

def parseMidiFile(file_name):

    """
    For parsing midi files.

    Parameters
    ==========
        file_name (string): the file path of the midi file to read.
        verbose (bool): whether you want to log parsing data
    """

    midi_file = open(file_name, "rb")
    byte_data = midi_file.read()
    midi_file.close
    number_bytes_in_file = len(byte_data)

    # Parse Midi Header

    if not isMidiFile(byte_data):
        raise Exception("Source file is not a midi file")
    number_tracks = getNumberOfTracks(byte_data)
    ticks_per_beat = getTicksPerBeat(byte_data)
    tracks: list[Track] = []

    # Parse Tracks

    index = 14
    for track_number in range(number_tracks):
        if not isTrackStart(byte_data, index):
            raise Exception(f"Parse error: the byte at the current index ({index}) doesn't represent the beginning of a track")
        index += 8
        new_track = Track(track_number, ticks_per_beat)
        current_running_status = RunningStatus.NONE
        while index < number_bytes_in_file:
            delta_time, delta_time_byte_length = getDeltaTime(byte_data, index)
            new_track.append(TimeEvent(delta_time))
            index += delta_time_byte_length

            # -----------
            # Meta Events
            # -----------

            if isMetaEvent(byte_data, index):
                current_running_status = RunningStatus.NONE

                if isTrackName(byte_data, index):
                    name, name_byte_length = getTrackName(byte_data, index)
                    new_track.append(TrackNameEvent(name))
                    index += name_byte_length

                elif isMidiPort(byte_data, index):
                    port = byte_data[index + 3]
                    new_track.append(MidiPortEvent(port))
                    index += 4

                elif isTrackEnd(byte_data, index):
                    new_track.append(TrackEndEvent())
                    index += 3
                    break

                elif isTempoChange(byte_data, index):
                    microseconds_per_beat = concatenateBytes(byte_data[index + 3:index + 6])
                    new_track.append(TempoEvent(microseconds_per_beat))
                    index += 6

                elif isTimeSignature(byte_data, index):
                    numerator = byte_data[index + 3]
                    denominator = 2 ** byte_data[index + 4]
                    new_track.append(TimeSignatureEvent(numerator, denominator))
                    index += 7

                elif isKeySignature(byte_data, index):
                    number_accidentals = convertBitStringToSignedInt(getBits(byte_data[index + 3]))
                    is_minor = (byte_data[index + 4] == 1)
                    new_track.append(KeySignatureEvent(number_accidentals, is_minor))
                    index += 5

            # ----------------
            # Channel-Specific
            # ----------------

            elif isNoteOff(byte_data, index):
                channel_number = byte_data[index] - 128
                note_number = byte_data[index + 1]
                velocity = byte_data[index + 2]
                new_track.append(NoteOffEvent(channel_number, note_number, velocity))
                current_running_status = RunningStatus.NOTE_OFF
                index += 3

            elif isNoteOn(byte_data, index):
                channel_number = byte_data[index] - 144
                note_number = byte_data[index + 1]
                velocity = byte_data[index + 2]
                new_track.append(NoteOnEvent(channel_number, note_number, velocity))
                current_running_status = RunningStatus.NOTE_ON
                index += 3

            elif isControlChange(byte_data, index):
                channel_number = byte_data[index] - 176
                control_number = byte_data[index + 1]
                value = byte_data[index + 2]
                new_track.append(ControlChangeEvent(channel_number, control_number, value))
                current_running_status = RunningStatus.CONTROL_CHANGE
                index += 3

            elif isProgramChange(byte_data, index):
                channel_number = byte_data[index] - 192
                program_number = byte_data[index + 1]
                new_track.append(ProgramChangeEvent(channel_number, program_number))
                current_running_status = RunningStatus.PROGRAM_CHANGE
                index += 2

            # -------------------------------
            # Channel-Specific Running Status
            # -------------------------------

            elif not current_running_status == RunningStatus.NONE:

                if current_running_status == RunningStatus.NOTE_OFF:
                    note_number = byte_data[index]
                    velocity = byte_data[index + 1]
                    new_track.append(NoteOffEvent(channel_number, note_number, velocity))
                    index += 2

                elif current_running_status == RunningStatus.NOTE_ON:
                    note_number = byte_data[index]
                    velocity = byte_data[index + 1]
                    new_track.append(NoteOnEvent(channel_number, note_number, velocity))
                    index += 2

                elif current_running_status == RunningStatus.CONTROL_CHANGE:
                    control_number = byte_data[index]
                    value = byte_data[index + 1]
                    new_track.append(ControlChangeEvent(channel_number, control_number, value))
                    index += 2

                elif current_running_status == RunningStatus.PROGRAM_CHANGE:
                    program_number = byte_data[index]
                    new_track.append(ProgramChangeEvent(channel_number, program_number))
                    index += 1

            # ----------------
            # Channel-Agnostic
            # ----------------

            elif isPan(byte_data, index):
                pan = byte_data[index + 1]
                new_track.append(Event(f"Pan: {pan}"))
                index += 2

            elif isReverb(byte_data, index):
                reverb = byte_data[index + 1]
                new_track.append(Event(f"Reverb: {reverb}"))
                index += 2

            elif isTremolo(byte_data, index):
                tremolo = byte_data[index + 1]
                new_track.append(Event(f"Tremolo: {tremolo}"))
                index += 2

            elif isChorus(byte_data, index):
                chorus = byte_data[index + 1]
                new_track.append(Event(f"Chorus: {chorus}"))
                index += 2

            else:
                raise Exception(f"Parse error: unrecognized midi event at byte {index}: {getBits(byte_data[index])}")

        tracks.append(new_track)

    return tracks

def condenseMidiTracks(tracks: list[Track]):

    for track in tracks:
        track.removeNullDeltaTimeEvents()
        track.removeAllEventsOfType(ControlChangeEvent)
        track.removeAllEventsOfType(KeySignatureEvent)
        track.removeAllEventsOfType(MidiPortEvent)
        track.removeAllEventsOfType(ProgramChangeEvent)
        track.removeAllEventsOfType(TrackNameEvent)
        track.convertNullNoteOnToNoteOff()
        track.convertDeltaTimeToElapsedTime()

    for track in tracks[1:]:
        tracks[0].mergeTracks(track)

    return tracks[0]