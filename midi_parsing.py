import numpy as np
from enum import Enum, auto
import binary_tools as bt
from midi_elements import *

class EventType(Enum):
    DELTA_T = auto()
    OTHER = auto()
    TRACK_START = auto()

class RunningStatus(Enum):
    CONTROL_CHANGE = auto()
    NONE = auto()
    NOTE_END = auto()
    NOTE_START = auto()
    PROGRAM_CHANGE = auto()

def extractVariableLengthQuantity(byte_data, index):

    is_looking_for_end = True
    vlq_bits = ""
    vlq_length = 1

    while is_looking_for_end:
        current_bits = bt.getBits(byte_data[index])
        vlq_bits += current_bits[1:]
        if current_bits[0] == "1":
            index += 1
            vlq_length += 1
        else:
            is_looking_for_end = False

    vlq_value = bt.convertBitStringToInt(vlq_bits)

    return [vlq_value, vlq_length]

def isMidiFile(byte_data):

    if byte_data[0] == ord("M") and byte_data[1] == ord("T") and byte_data[2] == ord("h") and byte_data[3] == ord("d"):
        return True
    else:
        return False

def isTrackStart(byte_data, index):

    if byte_data[index] == ord("M") and byte_data[index + 1] == ord("T") and byte_data[index + 2] == ord("r") and byte_data[index + 3] == ord("k"):
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

def isEndTrack(byte_data, index):

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

def isChannelNoteEnd(byte_data, index):

    bits = bt.getBits(byte_data[index])

    if bits[0:4] == "1000":
        return True
    else:
        return False

def isChannelNoteStart(byte_data, index):

    bits = bt.getBits(byte_data[index])

    if bits[0:4] == "1001":
        return True
    else:
        return False

def isChannelControlChange(byte_data, index):

    bits = bt.getBits(byte_data[index])

    if bits[0:4] == "1011":
        return True
    else:
        return False

def isChannelProgramChange(byte_data, index):

    bits = bt.getBits(byte_data[index])

    if bits[0:4] == "1100":
        return True
    else:
        return False

def isControlPanChange(byte_data, index):

    if hex(byte_data[index]) == "0xa":
        return True
    else:
        return False

def isControlReverbChange(byte_data, index):

    if hex(byte_data[index]) == "0x5b":
        return True
    else:
        return False

def isControlTremoloChange(byte_data, index):

    if hex(byte_data[index]) == "0x5c":
        return True
    else:
        return False

def isControlChorusChange(byte_data, index):

    if hex(byte_data[index]) == "0x5d":
        return True
    else:
        return False

def getNumberOfChannels(byte_data):

    channel_type = byte_data[9]
    if channel_type == 0:
        channels = 1
    elif channel_type == 1 or channel_type == 2:
        channels = bt.concatenateBytes(byte_data[10:12])

    return channels

# def getChannelOrder(byte_data):

#     bytes_to_skip = 1
#     next_event = EventType.TRACK_START
#     channel_number = None
#     channel_order = []

#     for i in range(len(byte_data)):

#         if bytes_to_skip > 1:
#             bytes_to_skip -= 1

#         elif next_event == EventType.TRACK_START and isTrackStart(byte_data, i):
#             bytes_to_skip = 8
#             next_event = EventType.DELTA_T

#         elif next_event == EventType.DELTA_T:
#             vlq_value, vlq_length = extractVariableLengthQuantity(byte_data, i)
#             bytes_to_skip = vlq_length
#             next_event = EventType.OTHER

#         elif next_event == EventType.OTHER:

#             # ------------
#             # meta events:
#             # ------------

#             if isTrackName(byte_data, i):
#                 vlq_value, vlq_length = extractVariableLengthQuantity(byte_data, (i + 2))
#                 chunk_length = vlq_value
#                 bytes_to_skip = 2 + vlq_length + chunk_length
#                 next_event = EventType.DELTA_T

#             elif isMidiPort(byte_data, i):
#                 bytes_to_skip = 4
#                 next_event = EventType.DELTA_T

#             elif isEndTrack(byte_data, i):
#                 bytes_to_skip = 3
#                 next_event = EventType.TRACK_START

#             elif isTempoChange(byte_data, i):
#                 bytes_to_skip = 6
#                 next_event = EventType.DELTA_T

#             elif isTimeSignature(byte_data, i):
#                 bytes_to_skip = 7
#                 next_event = EventType.DELTA_T

#             elif isKeySignature(byte_data, i):
#                 bytes_to_skip = 5
#                 next_event = EventType.DELTA_T

#             # -----------------------
#             # channel voice messages:
#             # -----------------------

#             elif isChannelNoteEnd(byte_data, i):
#                 channel_number = byte_data[i] - 128
#                 channel_order.append(channel_number)
#                 bytes_to_skip = 3
#                 next_event = EventType.TRACK_START

#             elif isChannelNoteStart(byte_data, i):
#                 channel_number = byte_data[i] - 144
#                 channel_order.append(channel_number)
#                 bytes_to_skip = 3
#                 next_event = EventType.TRACK_START

#             elif isChannelControlChange(byte_data, i):
#                 channel_number = byte_data[i] - 176
#                 channel_order.append(channel_number)
#                 bytes_to_skip = 3
#                 next_event = EventType.TRACK_START

#             elif isChannelProgramChange(byte_data, i):
#                 channel_number = byte_data[i] - 192
#                 channel_order.append(channel_number)
#                 bytes_to_skip = 2
#                 next_event = EventType.TRACK_START

#             # -------------------------
#             # midi controller messages:
#             # -------------------------

#             elif isControlPanChange(byte_data, i):
#                 bytes_to_skip = 2
#                 next_event = EventType.DELTA_T

#             elif isControlReverbChange(byte_data, i):
#                 bytes_to_skip = 2
#                 next_event = EventType.DELTA_T

#             elif isControlTremoloChange(byte_data, i):
#                 bytes_to_skip = 2
#                 next_event = EventType.DELTA_T

#             elif isControlChorusChange(byte_data, i):
#                 bytes_to_skip = 2
#                 next_event = EventType.DELTA_T

#     return channel_order

def getTicksPerBeat(byte_data):

    bits = bt.getBits(byte_data[12])
    if bits[0] == "0":
        ticks_per_beat = bt.concatenateBytes(byte_data[12:14])
        return ticks_per_beat
    else:
        raise Exception("don\'t know how to handle this time format")

def parseMidiFile(file_name, verbose):

    """
    For parsing midi files into easy to use arrays of notes.

    Parameters
    ==========
        file_name (string): the file path of the midi file to read.
        verbose (bool): whether you want to log parsing data
    """

    midi_file = open(file_name, "rb")
    byte_data = midi_file.read()
    midi_file.close
    number_bytes_in_file = len(byte_data)

    if not isMidiFile(byte_data):
        raise Exception("source file is not a midi file")

    channels = getNumberOfChannels(byte_data)
    ticks_per_beat = getTicksPerBeat(byte_data)

    bytes_to_skip = 0
    current_running_status = RunningStatus.NONE
    next_event = EventType.TRACK_START
    tracks = []
    track_index = 0

    for i in range(14, number_bytes_in_file):

        if bytes_to_skip > 1:
            bytes_to_skip -= 1

        elif next_event == EventType.TRACK_START and isTrackStart(byte_data, i):
            tracks.append(Track(track_index))
            bytes_to_skip = 8
            next_event = EventType.DELTA_T

        elif next_event == EventType.DELTA_T:
            vlq_value, vlq_length = extractVariableLengthQuantity(byte_data, i)
            delta_t = vlq_value
            bytes_to_skip = vlq_length
            tracks[track_index].append(TimeDelta(delta_t))
            next_event = EventType.OTHER

        elif next_event == EventType.OTHER:

            # ------------
            # meta events:
            # ------------

            if isTrackName(byte_data, i):
                vlq_value, vlq_length = extractVariableLengthQuantity(byte_data, (i + 2))
                chunk_length = vlq_value
                bytes_to_skip = 2 + vlq_length + chunk_length
                next_event = EventType.DELTA_T

            elif isMidiPort(byte_data, i):
                bytes_to_skip = 4
                next_event = EventType.DELTA_T

            elif isEndTrack(byte_data, i):
                tracks[track_index].append(TrackEnd())
                bytes_to_skip = 3
                next_event = EventType.TRACK_START
                current_running_status = RunningStatus.NONE
                track_index += 1

            elif isTempoChange(byte_data, i):
                microseconds_per_beat = bt.concatenateBytes(byte_data[i + 3:i + 6])
                tracks[track_index].append(Tempo(microseconds_per_beat))
                bytes_to_skip = 6
                next_event = EventType.DELTA_T

            elif isTimeSignature(byte_data, i):
                numerator = byte_data[i + 3]
                denominator = 2 ** byte_data[i + 4]
                tracks[track_index].append(TimeSignature(numerator, denominator))
                bytes_to_skip = 7
                next_event = EventType.DELTA_T

            elif isKeySignature(byte_data, i):
                number_accidentals = byte_data[i + 3]
                is_minor = (byte_data[i + 4] == 1)
                tracks[track_index].append(KeySignature(number_accidentals, is_minor))
                bytes_to_skip = 5
                next_event = EventType.DELTA_T

            # -----------------------
            # channel voice messages:
            # -----------------------

            elif isChannelNoteEnd(byte_data, i):
                channel_number = byte_data[i] - 128
                note_value = byte_data[i + 1]
                tracks[track_index].append(NoteEnd(note_value))
                bytes_to_skip = 3
                next_event = EventType.DELTA_T
                current_running_status = RunningStatus.NOTE_END

            elif isChannelNoteStart(byte_data, i):
                channel_number = byte_data[i] - 144
                note_value = byte_data[i + 1]
                tracks[track_index].append(NoteStart(note_value))
                bytes_to_skip = 3
                next_event = EventType.DELTA_T
                current_running_status = RunningStatus.NOTE_START

            elif isChannelControlChange(byte_data, i):
                # channel_number = byte_data[i] - 176
                # control_number = byte_data[i + 1]
                # assigned_value = byte_data[i + 2]
                tracks[track_index].append(Event())
                bytes_to_skip = 3
                next_event = EventType.DELTA_T
                current_running_status = RunningStatus.CONTROL_CHANGE

            elif isChannelProgramChange(byte_data, i):
                # channel_number = byte_data[i] - 192
                # program_number = byte_data[i + 1]
                tracks[track_index].append(Event())
                bytes_to_skip = 2
                next_event = EventType.DELTA_T
                current_running_status = RunningStatus.PROGRAM_CHANGE

            # --------------------------------------
            # running status channel voice messages:
            # --------------------------------------

            elif current_running_status == RunningStatus.NOTE_END:
                note_value = byte_data[i]
                tracks[track_index].append(NoteEnd(note_value))
                bytes_to_skip = 2
                next_event = EventType.DELTA_T

            elif current_running_status == RunningStatus.NOTE_START:
                note_value = byte_data[i]
                tracks[track_index].append(NoteStart(note_value))
                bytes_to_skip = 2
                next_event = EventType.DELTA_T

            elif current_running_status == RunningStatus.CONTROL_CHANGE:
                # control_number = byte_data[i]
                # assigned_value = byte_data[i + 1]
                tracks[track_index].append(Event())
                bytes_to_skip = 2
                next_event = EventType.DELTA_T

            elif current_running_status == RunningStatus.PROGRAM_CHANGE:
                # program_number = byte_data[i]
                tracks[track_index].append(Event())
                bytes_to_skip = 1
                next_event = EventType.DELTA_T

            # -------------------------
            # midi controller messages:
            # -------------------------

            elif isControlPanChange(byte_data, i):
                # pan = byte_data[i + 1]
                tracks[track_index].append(Event())
                bytes_to_skip = 2
                next_event = EventType.DELTA_T

            elif isControlReverbChange(byte_data, i):
                # reverb = byte_data[i + 1]
                tracks[track_index].append(Event())
                bytes_to_skip = 2
                next_event = EventType.DELTA_T

            elif isControlTremoloChange(byte_data, i):
                # tremolo = byte_data[i + 1]
                tracks[track_index].append(Event())
                bytes_to_skip = 2
                next_event = EventType.DELTA_T

            elif isControlChorusChange(byte_data, i):
                # chorus = byte_data[i + 1]
                tracks[track_index].append(Event())
                bytes_to_skip = 2
                next_event = EventType.DELTA_T

    # sync = synchronizeEvents(notes_array, verbose, debug)
    # sync = convertTimesToDurations(sync, ticks_per_beat, verbose, debug)

    # return sync

    for track in tracks:
        print(track)

def synchronizeEvents(notes_array, verbose, debug):

    channels = len(notes_array)
    number_bytes_in_file = len(notes_array[0])

    # create an array to store "start" indices
    starts = np.zeros(len(notes_array), dtype = np.int64)
    # populate starts with indices of first note or tempo marking
    for j in range(len(notes_array)):
        for i in range(len(notes_array[j])):
            if notes_array[j][i][0] == "tempo" or type(notes_array[j][i][0]) != str:
                starts[j] = i
                break

    # create an array to store "end" indices
    ends = np.zeros(len(notes_array), dtype = np.int64)
    # populate ends with indices where "end" is found:
    for j in range(len(notes_array)):
        for i in range(len(notes_array[j])):
            if notes_array[j][i][0] == "end":
                ends[j] = i
                break

    # group delta t's with notes and tempo changes
    for j in range(len(notes_array)):
        # start at the end, go backward to element 1
        for i in range(ends[j], starts[j], -1):
            # if this event is not a note or tempo change
            if type(notes_array[j][i][0]) == str and notes_array[j][i - 1][0] != "tempo":
                notes_array[j][i - 1][2] += notes_array[j][i][2]
                notes_array[j][i][2] = 0

    # switch from delta time to elapsed time
    for j in range(len(notes_array)):
        for i in range(2, ends[j]):
            notes_array[j][i][2] += notes_array[j][i - 1][2]

    # switch from end times to start times
    for j in range(len(notes_array)):
        for i in range(ends[j], starts[j] - 1, -1):
            notes_array[j][i][2] = notes_array[j][i - 1][2]

    # change volume to on/off
    for j in range(len(notes_array)):
        for i in range(1, ends[j]):
            if notes_array[j][i][1] != 0 and isinstance(notes_array[j][i][0], str) == False:
                notes_array[j][i][1] = 1

    # print out notes
    if verbose:
        debug.write("\nnotes\n")
        for j in range(len(notes_array)):
            debug.write("\n")
            for i in range(ends[j] + 1):
                debug.write(str(notes_array[j][i]) + "\n")

    # create list for filling with synchronized notes
    sync = np.zeros((channels + 1, number_bytes_in_file, 3), dtype = object)

    # create list containing time stamps to step through as we sync notes
    times = [0]
    for j in range(len(notes_array)):
        for i in range(1, ends[j] + 1):
            times.append(notes_array[j][i][2])

    # remove duplicates and sort
    times = sorted(list(set(times)))

    # populating sync
    position = -1
    starting_a_row = -1
    pick_up_from = np.ones(channels, dtype = np.int64)

    # check at every possible time stamp
    for i in times:

        # check each channel
        for j in range(len(notes_array)):

            # check each row in the channel
            for k in range(pick_up_from[j], ends[j] + 1):

                # if the time in notes matches i, and it's a note
                if notes_array[j][k][2] == i and type(notes_array[j][k][0]) != str:

                    # if we've just gotten to this time stamp, make sure that we're beginning a new row in sync
                    if starting_a_row != i:
                        starting_a_row = i
                        position += 1
                        # make sure time info is correct in all columns
                        for m in range(len(sync)):
                            sync[m][position][2] = i

                    # copy notes over to sync
                    sync[j][position] = notes_array[j][k]

                # if the time in notes matches i, and it is a tempo change
                elif notes_array[j][k][2] == i and notes_array[j][k][0] == "tempo":

                    # if we've just gotten to this time stamp, make sure that we're beginning a new row in sync
                    if starting_a_row != i:
                        starting_a_row = i
                        position += 1
                        # make sure time info is correct in all columns
                        for m in range(len(sync)):
                            sync[m][position][2] = i

                    # copy notes over to sync
                    sync[-1][position] = notes_array[j][k]

                # if this is the end of a track
                elif notes_array[j][k][2] == i and notes_array[j][k][0] == "end":

                    # if we've just gotten to this time stamp, make sure that we're beginning a new row in sync
                    if starting_a_row != i:
                        starting_a_row = i
                        position += 1
                        # make sure time info is correct in all columns
                        for m in range(len(sync)):
                            sync[m][position][2] = i

                    # copy notes over to sync
                    sync[j][position] = notes_array[j][k]

                # if the time stamp is greater than i, then we've gone too far and should stop
                elif notes_array[j][k][2] > i:
                    # record where to pick up from on the next go through (to save time)
                    pick_up_from[j] = k
                    break

    # # determine the last significant row of sync
    ends_found = 0
    for i in range(number_bytes_in_file):
        for j in range(channels):
            if sync[j][i][0] == "end":
                sync_last = i
                ends_found += 1
                if ends_found == channels:
                    break

    sync = sync[:len(sync), :sync_last]

    return sync

def convertTimesToDurations(sync, ticks_per_beat, verbose, debug):

    lenth_sync = len(sync[0])

    # print out sync with time stamps
    if verbose:
        current_width = 0
        column_width = 20
        debug.write("\nsync with time stamps\n")
        for i in range(len(sync[0])):
            debug.write("\n")
            for j in range(len(sync)):
                current_width = len(str(sync[j][i]))
                debug.write(str(sync[j][i]))
                if current_width < column_width:
                    for k in range(current_width, column_width):
                        debug.write(" ")
        debug.write("\n")

    # switch times to durations
    # for each column:
    for j in range(len(sync)):
        # for each triple
        for i in range(lenth_sync - 1):
            # each time entry equals the next time minus the current one
            sync[j][i][2] = sync[j][i + 1][2] - sync[j][i][2]
    # change the last durations to 0
    for j in range(len(sync)):
        sync[j][-1][2] = 0

    current_mspb = sync[-1][0][1]
    # convert durations to milliseconds
    # for each column:
    for j in range(len(sync) - 1):
        # for each triple
        for i in range(lenth_sync):
            # check to see if the tempo has changed
            if sync[-1][i][0] == "tempo":
                current_mspb = sync[-1][i][1]
            # 1000 for milliseconds
            temp = ticks_per_beat * 1000
            temp = current_mspb / temp
            temp = temp * sync[j][i][2]
            temp = np.float64(temp)
            sync[j][i][2] = temp

    # print out sync with durations
    if verbose:
        current_width = 0
        column_width = 20
        debug.write("\nsync with durations\n")
        for i in range(len(sync[0])):
            debug.write("\n")
            for j in range(len(sync)):
                string = f"[{sync[j][i][0]} {sync[j][i][1]} {np.around(sync[j][i][2], 2)}]"
                debug.write(string)
                current_width = len(string)
                if current_width < column_width:
                    for k in range(current_width, column_width):
                        debug.write(" ")

    # close debug file
    if verbose:
        debug.close

    return sync