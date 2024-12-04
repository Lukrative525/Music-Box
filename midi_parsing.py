import numpy as np
from enum import Enum, auto
import binary_tools as bt

class EventType(Enum):
    DELTA_T = auto()
    OTHER = auto()
    TRACK_START = auto()

class RunningStatus(Enum):
    NONE = auto()
    NOTE_END = auto()
    NOTE_START = auto()
    CONTROL_CHANGE = auto()
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

def isTempoMarking(byte_data, index):

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

def getChannelOrder(byte_data):

    bytes_to_skip = 1
    next_event_type = EventType.TRACK_START
    channel_number = None
    is_looking_for_track_start = True
    channel_order = []

    for i in range(len(byte_data)):

        if is_looking_for_track_start:
            if isTrackStart(byte_data, i):
                bytes_to_skip = 8
                next_event_type = EventType.DELTA_T
                is_looking_for_track_start = False

        elif not is_looking_for_track_start:

            if bytes_to_skip > 1:
                bytes_to_skip -= 1

            elif next_event_type == EventType.DELTA_T:
                vlq_value, vlq_length = extractVariableLengthQuantity(byte_data, i)
                bytes_to_skip = vlq_length
                next_event_type = EventType.OTHER

            elif next_event_type == EventType.OTHER:

                # ------------
                # meta events:
                # ------------

                if isTrackName(byte_data, i):
                    vlq_value, vlq_length = extractVariableLengthQuantity(byte_data, (i + 2))
                    chunk_length = vlq_value
                    bytes_to_skip = 2 + vlq_length + chunk_length
                    next_event_type = EventType.DELTA_T

                elif isMidiPort(byte_data, i):
                    bytes_to_skip = 4
                    next_event_type = EventType.DELTA_T

                elif isEndTrack(byte_data, i):
                    bytes_to_skip = 3
                    next_event_type = EventType.DELTA_T

                elif isTempoMarking(byte_data, i):
                    bytes_to_skip = 6
                    next_event_type = EventType.DELTA_T

                elif isTimeSignature(byte_data, i):
                    bytes_to_skip = 7
                    next_event_type = EventType.DELTA_T

                elif isKeySignature(byte_data, i):
                    bytes_to_skip = 5
                    next_event_type = EventType.DELTA_T

                # -----------------------
                # channel voice messages:
                # -----------------------

                elif isChannelNoteEnd(byte_data, i):
                    channel_number = byte_data[i] - 128
                    channel_order.append(channel_number)
                    bytes_to_skip = 3
                    next_event_type = EventType.DELTA_T
                    is_looking_for_track_start = True

                elif isChannelNoteStart(byte_data, i):
                    channel_number = byte_data[i] - 144
                    channel_order.append(channel_number)
                    bytes_to_skip = 3
                    next_event_type = EventType.DELTA_T
                    is_looking_for_track_start = True

                elif isChannelControlChange(byte_data, i):
                    channel_number = byte_data[i] - 176
                    channel_order.append(channel_number)
                    bytes_to_skip = 3
                    next_event_type = EventType.DELTA_T
                    is_looking_for_track_start = True

                elif isChannelProgramChange(byte_data, i):
                    channel_number = byte_data[i] - 192
                    channel_order.append(channel_number)
                    bytes_to_skip = 2
                    next_event_type = EventType.DELTA_T
                    is_looking_for_track_start = True

                # -------------------------
                # midi controller messages:
                # -------------------------

                elif isControlPanChange(byte_data, i):
                    bytes_to_skip = 2
                    next_event_type = EventType.DELTA_T

                elif isControlReverbChange(byte_data, i):
                    bytes_to_skip = 2
                    next_event_type = EventType.DELTA_T

                elif isControlTremoloChange(byte_data, i):
                    bytes_to_skip = 2
                    next_event_type = EventType.DELTA_T

                elif isControlChorusChange(byte_data, i):
                    bytes_to_skip = 2
                    next_event_type = EventType.DELTA_T

    return(channel_order)

def getTicksPerBeat(byte_data):

    bits = bt.getBits(byte_data[12])
    if bits[0] == "0":
        ticks_per_beat = bt.concatenateBytes(byte_data[12:14])
        return ticks_per_beat
    else:
        raise Exception("don\'t know how to handle this time format")

def parse(file_name, verbose):

    """
    For parsing midi files into easy to use arrays of notes.

    Parameters
    ==========
        file_name (string): the file path of the midi file to read.
        verbose (bool): whether you want to log parsing data
    """

    if verbose:
        debug = open("debug.txt", "w")

    midi_file = open(file_name, "rb")
    byte_data = midi_file.read()
    midi_file.close
    number_bytes_in_file = len(byte_data)

    if not isMidiFile(byte_data):
        raise Exception("source file is not a midi file")

    channels = getNumberOfChannels(byte_data)
    if verbose:
        debug.write(f"number of channels: {channels}\n")

    channel_order = getChannelOrder(byte_data)
    if verbose:
        debug.write(f"channel order: {channel_order}\n")

    # create list to store note values
    notes = np.zeros((channels, number_bytes_in_file, 3), dtype = object)
    for i in range(channels):
        notes[i][0][0] = f"channel {i}"

    #  extract ticks per beat from header:
    ticks_per_beat = getTicksPerBeat(byte_data)
    if verbose:
        debug.write(f"ticks per beat: {ticks_per_beat}\n")

    # start parsing track chunks
    bytes_to_skip = 0
    next_event_type = EventType.TRACK_START
    new_note = np.zeros(3, dtype = object)
    new_note[0] = -1
    channel_index = 0
    channel_number = channel_order[channel_index]
    current_running_status = RunningStatus.NONE
    position = 1

    for i in range(14, number_bytes_in_file):

        if bytes_to_skip > 1:
            bytes_to_skip -= 1

        elif isTrackStart(byte_data, i):
            if verbose:
                debug.write("starting next track\n")
            new_note[0] = "new"
            bytes_to_skip = 8
            next_event_type = EventType.DELTA_T

        elif next_event_type == EventType.DELTA_T:
            vlq_value, vlq_length = extractVariableLengthQuantity(byte_data, i)
            delta_t = vlq_value
            bytes_to_skip = vlq_length
            if verbose:
                debug.write(f"delta t: {delta_t}\n")
            new_note[2] = delta_t
            for j in range(3):
                notes[channel_number][position][j] = new_note[j]
            position += 1
            new_note = [-1, 0, 0]
            next_event_type = EventType.OTHER

        elif next_event_type == EventType.OTHER:

            # ------------
            # meta events:
            # ------------

            if isTrackName(byte_data, i):
                vlq_value, vlq_length = extractVariableLengthQuantity(byte_data, (i + 2))
                chunk_length = vlq_value
                name = ""
                for k in range(chunk_length):
                    byte_value = byte_data[i + 2 + vlq_length + k]
                    if byte_value != 0:
                        name += chr(byte_value)
                if verbose:
                    debug.write(f"track name: {name}\n")
                new_note[0] = "name"
                bytes_to_skip = 2 + vlq_length + chunk_length
                next_event_type = EventType.DELTA_T

            elif isMidiPort(byte_data, i):
                port = byte_data[i + 3]
                if verbose:
                    debug.write(f"port: {port}\n")
                new_note[0] = "port"
                bytes_to_skip = 4
                next_event_type = EventType.DELTA_T

            elif isEndTrack(byte_data, i):
                if verbose:
                    debug.write("end track\n")
                new_note[0] = "end"
                for j in range(3):
                    notes[channel_number][position][j] = new_note[j]
                for j in range(1,3):
                    new_note[j] = 0
                new_note[0] = -1
                bytes_to_skip = 3
                next_event_type = EventType.DELTA_T
                current_running_status = RunningStatus.NONE
                position = 1
                if channel_index < channels - 1:
                    channel_index += 1
                    channel_number = channel_order[channel_index]

            elif isTempoMarking(byte_data, i):
                mspb = byte_data[i + 3]*2**16 + byte_data[i + 4]*2**8 + byte_data[i + 5]
                if verbose:
                    debug.write(f"microseconds per beat: {mspb}\n")
                new_note[0] = "tempo"
                new_note[1] = mspb
                bytes_to_skip = 6
                next_event_type = EventType.DELTA_T

            elif isTimeSignature(byte_data, i):
                numerator = byte_data[i + 3]
                denominator = 2**byte_data[i + 4]
                if verbose:
                    debug.write(f"time signature: {numerator}/{denominator}\n")
                new_note[0] = "time"
                bytes_to_skip = 7
                next_event_type = EventType.DELTA_T

            elif isKeySignature(byte_data, i):
                if verbose:
                    debug.write("key signature\n")
                new_note[0] = "key"
                bytes_to_skip = 5
                next_event_type = EventType.DELTA_T

            # -----------------------
            # channel voice messages:
            # -----------------------

            elif isChannelNoteEnd(byte_data, i):
                channel_number = byte_data[i] - 128
                note = byte_data[i + 1]
                volume = byte_data[i + 2]
                if verbose:
                    debug.write(f"channel number: {channel_number}\n")
                    debug.write(f"note number: {note}\n")
                    debug.write(f"note volume: {volume}\n")
                new_note[0] = note
                new_note[1] = volume
                bytes_to_skip = 3
                next_event_type = EventType.DELTA_T
                current_running_status = RunningStatus.NOTE_END

            elif isChannelNoteStart(byte_data, i):
                channel_number = byte_data[i] - 144
                note = byte_data[i + 1]
                volume = byte_data[i + 2]
                if verbose:
                    debug.write(f"channel number: {channel_number}\n")
                    debug.write(f"note number: {note}\n")
                    debug.write(f"note volume: {volume}\n")
                new_note[0] = note
                new_note[1] = volume
                bytes_to_skip = 3
                next_event_type = EventType.DELTA_T
                current_running_status = RunningStatus.NOTE_START

            elif isChannelControlChange(byte_data, i):
                channel_number = byte_data[i] - 176
                control_number = byte_data[i + 1]
                assigned_value = byte_data[i + 2]
                if verbose:
                    debug.write(f"channel number: {channel_number}\n")
                    debug.write(f"control number: {control_number}\n")
                    debug.write(f"assigned value: {assigned_value}\n")
                new_note[0] = "control"
                bytes_to_skip = 3
                next_event_type = EventType.DELTA_T
                current_running_status = RunningStatus.CONTROL_CHANGE

            elif isChannelProgramChange(byte_data, i):
                channel_number = byte_data[i] - 192
                program_number = byte_data[i + 1]
                if verbose:
                    debug.write(f"channel number: {channel_number}\n")
                    debug.write(f"program number: {program_number}\n")
                new_note[0] = "program"
                bytes_to_skip = 2
                next_event_type = EventType.DELTA_T
                current_running_status = RunningStatus.PROGRAM_CHANGE

            # --------------------------------------
            # running status channel voice messages:
            # --------------------------------------

            elif current_running_status == RunningStatus.NOTE_END:
                note = byte_data[i]
                volume = byte_data[i + 1]
                if verbose:
                    debug.write(f"implied channel number: {channel_number}\n")
                    debug.write(f"note number: {note}\n")
                    debug.write(f"note volume: {volume}\n")
                new_note[0] = note
                new_note[1] = volume
                bytes_to_skip = 2
                next_event_type = EventType.DELTA_T

            elif current_running_status == RunningStatus.NOTE_START:
                note = byte_data[i]
                volume = byte_data[i + 1]
                if verbose:
                    debug.write(f"implied channel number: {channel_number}\n")
                    debug.write(f"note number: {note}\n")
                    debug.write(f"note volume: {volume}\n")
                new_note[0] = note
                new_note[1] = volume
                bytes_to_skip = 2
                next_event_type = EventType.DELTA_T

            elif current_running_status == RunningStatus.CONTROL_CHANGE:
                control_number = byte_data[i]
                assigned_value = byte_data[i + 1]
                if verbose:
                    debug.write(f"implied channel number: {channel_number}\n")
                    debug.write(f"control number: {control_number}\n")
                    debug.write(f"assigned value: {assigned_value}\n")
                new_note[0] = "control"
                bytes_to_skip = 2
                next_event_type = EventType.DELTA_T

            elif current_running_status == RunningStatus.PROGRAM_CHANGE:
                program_number = byte_data[i]
                if verbose:
                    debug.write(f"implied channel number: {channel_number}\n")
                    debug.write(f"program number: {program_number}\n")
                new_note[0] = "program"
                bytes_to_skip = 1
                next_event_type = EventType.DELTA_T

            # -------------------------
            # midi controller messages:
            # -------------------------

            elif isControlPanChange(byte_data, i):
                pan = byte_data[i + 1]
                if verbose:
                    debug.write(f"pan: {pan}\n")
                new_note[0] = "pan"
                bytes_to_skip = 2
                next_event_type = EventType.DELTA_T

            elif isControlReverbChange(byte_data, i):
                depth = byte_data[i + 1]
                if verbose:
                    debug.write(f"reverb: {depth}\n")
                new_note[0] = "reverb"
                bytes_to_skip = 2
                next_event_type = EventType.DELTA_T

            elif isControlTremoloChange(byte_data, i):
                depth = byte_data[i + 1]
                if verbose:
                    debug.write(f"tremolo: {depth}\n")
                new_note[0] = "tremolo"
                bytes_to_skip = 2
                next_event_type = EventType.DELTA_T

            elif isControlChorusChange(byte_data, i):
                depth = byte_data[i + 1]
                if verbose:
                    debug.write(f"chorus: {depth}\n")
                new_note[0] = "chorus"
                bytes_to_skip = 2
                next_event_type = EventType.DELTA_T

        if verbose:
            debug.write(f"byte[{i}] is {byte_data[i]}\n")

    # create an array to store "start" indices
    starts = np.zeros(len(notes), dtype = np.int64)
    # populate starts with indices of first note or tempo marking
    for j in range(len(notes)):
        for i in range(len(notes[j])):
            if notes[j][i][0] == "tempo" or type(notes[j][i][0]) != str:
                starts[j] = i
                break

    # create an array to store "end" indices
    ends = np.zeros(len(notes), dtype = np.int64)
    # populate ends with indices where "end" is found:
    for j in range(len(notes)):
        for i in range(len(notes[j])):
            if notes[j][i][0] == "end":
                ends[j] = i
                break

    # group delta t's with notes and tempo changes
    for j in range(len(notes)):
        # start at the end, go backward to element 1
        for i in range(ends[j], starts[j], -1):
            # if this event is not a note or tempo change
            if type(notes[j][i][0]) == str and notes[j][i - 1][0] != "tempo":
                notes[j][i - 1][2] += notes[j][i][2]
                notes[j][i][2] = 0

    # switch from delta time to elapsed time
    for j in range(len(notes)):
        for i in range(2, ends[j]):
            notes[j][i][2] += notes[j][i - 1][2]

    # switch from end times to start times
    for j in range(len(notes)):
        for i in range(ends[j], starts[j] - 1, -1):
            notes[j][i][2] = notes[j][i - 1][2]

    # change volume to on/off
    for j in range(len(notes)):
        for i in range(1, ends[j]):
            if notes[j][i][1] != 0 and isinstance(notes[j][i][0], str) == False:
                notes[j][i][1] = 1

    # print out notes
    if verbose:
        debug.write("\nnotes\n")
        for j in range(len(notes)):
            debug.write("\n")
            for i in range(ends[j] + 1):
                debug.write(str(notes[j][i]) + "\n")

    # create list for filling with synchronized notes
    sync = np.zeros((channels + 1, number_bytes_in_file, 3), dtype = object)

    # create list containing time stamps to step through as we sync notes
    times = [0]
    for j in range(len(notes)):
        for i in range(1, ends[j] + 1):
            times.append(notes[j][i][2])

    # remove duplicates and sort
    times = sorted(list(set(times)))

    # populating sync
    position = -1
    starting_a_row = -1
    pick_up_from = np.ones(channels, dtype = np.int64)

    # check at every possible time stamp
    for i in times:

        # check each channel
        for j in range(len(notes)):

            # check each row in the channel
            for k in range(pick_up_from[j], ends[j] + 1):

                # if the time in notes matches i, and it's a note
                if notes[j][k][2] == i and type(notes[j][k][0]) != str:

                    # if we've just gotten to this time stamp, make sure that we're beginning a new row in sync
                    if starting_a_row != i:
                        starting_a_row = i
                        position += 1
                        # make sure time info is correct in all columns
                        for m in range(len(sync)):
                            sync[m][position][2] = i

                    # copy notes over to sync
                    sync[j][position] = notes[j][k]

                # if the time in notes matches i, and it is a tempo change
                elif notes[j][k][2] == i and notes[j][k][0] == "tempo":

                    # if we've just gotten to this time stamp, make sure that we're beginning a new row in sync
                    if starting_a_row != i:
                        starting_a_row = i
                        position += 1
                        # make sure time info is correct in all columns
                        for m in range(len(sync)):
                            sync[m][position][2] = i

                    # copy notes over to sync
                    sync[-1][position] = notes[j][k]

                # if this is the end of a track
                elif notes[j][k][2] == i and notes[j][k][0] == "end":

                    # if we've just gotten to this time stamp, make sure that we're beginning a new row in sync
                    if starting_a_row != i:
                        starting_a_row = i
                        position += 1
                        # make sure time info is correct in all columns
                        for m in range(len(sync)):
                            sync[m][position][2] = i

                    # copy notes over to sync
                    sync[j][position] = notes[j][k]

                # if the time stamp is greater than i, then we've gone too far and should stop
                elif notes[j][k][2] > i:
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
        for i in range(sync_last - 1):
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
        for i in range(sync_last):
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

    return(sync)