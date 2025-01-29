from __future__ import annotations
from enum import Enum
from math import floor

microseconds_per_second = 1e6

note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def convertMidiToPitchNotation(note_number):

    """
    For converting midi note numbers (e.g. 69) to scientific pitch notation (e.g. A4)
    """

    octave = int(floor(note_number / 12) - 1)
    note = note_names[note_number % 12]

    return note + str(octave)

class TimeEventType(Enum):
    DELTA = "delta"
    ELAPSED = "elapsed"

class Track(list):
    def __init__(self, track_number, ticks_per_beat):
        self.track_number = track_number
        self.ticks_per_beat = ticks_per_beat

        self.channels = set()

    def append(self, new_event):
        if isinstance(new_event, Event) and not any(isinstance(event, TrackEndEvent) for event in self):
            super().append(new_event)
            self.updateChannelSet(new_event)

    def convertDeltaTimeToElapsedTime(self):

        if not self.hasTimeEventsAllOfType(TimeEventType.DELTA):
            raise Exception(f"Cannot perform time event conversion to type \"{TimeEventType.ELAPSED.value}\": track already contains time events of this type.")

        elapsed_time = 0
        for event in self:
            if isinstance(event, TimeEvent):
                elapsed_time = event.value + elapsed_time
                event.value = elapsed_time
                event.time_event_type = TimeEventType.ELAPSED

    def convertElapsedTimeToDeltaTime(self):

        if not self.hasTimeEventsAllOfType(TimeEventType.ELAPSED):
            raise Exception(f"Cannot perform time event conversion to type \"{TimeEventType.DELTA.value}\": track already contains time events of this type.")

        previous_elapsed_time = 0
        for event in self:
            if isinstance(event, TimeEvent):
                delta_time = event.value - previous_elapsed_time
                previous_elapsed_time = event.value
                event.value = delta_time
                event.time_event_type = TimeEventType.DELTA

    def convertNullNoteOnToNoteOff(self):
        for i, event in enumerate(self):
            if isinstance(event, NoteOnEvent) and event.velocity == 0:
                self[i] = NoteOffEvent(event.channel_index, event.note_number, event.velocity)

    def convertTicksToSeconds(self):

        if not self.hasTempoEvents():
            raise Exception("Cannot convert ticks to microseconds because track has no tempo events.")
        elif not self.hasTimeEventsAllOfType(TimeEventType.DELTA):
            raise Exception(f"Cannot convert ticks to microseconds because track contains time events of type \"{TimeEventType.ELAPSED.value}\".")

        microseconds_per_beat = 0
        for event in self:
            if isinstance(event, TimeEvent):
                event.value = event.value / self.ticks_per_beat * microseconds_per_beat / microseconds_per_second
            elif isinstance(event, TempoEvent):
                microseconds_per_beat = event.microseconds_per_beat

    def hasTempoEvents(self):
        for event in self:
            if isinstance(event, TempoEvent):
                return True

        return False

    def hasTimeEventsAllOfType(self, desired_type=TimeEventType.DELTA):
        for event in self:
            if isinstance(event, TimeEvent):
                if not event.time_event_type == desired_type:
                    return False

        return True

    def insert(self, index, new_event):
        super().insert(index, new_event)
        self.updateChannelSet(new_event)

    def mergeTracks(self, source: Track):

        if not self.hasTimeEventsAllOfType(TimeEventType.ELAPSED) or not source.hasTimeEventsAllOfType(TimeEventType.ELAPSED):
            raise Exception(f"To perform a track merge, both tracks' time events must all be of type \"{TimeEventType.ELAPSED.value}\".")

        if not isinstance(self[-1], TrackEndEvent):
            raise Exception("Target track for merge is missing a track end event.")
        elif not isinstance(source[-1], TrackEndEvent):
            raise Exception("Source track for merge is missing a track end event.")

        index = 0
        while True:
            while index < len(self) and not isinstance(self[index], TimeEvent):
                index += 1
            if index >= len(self):
                break

            while len(source) > 1 and not isinstance(source[0], TimeEvent):
                self.insert(index, source.pop(0))
                index += 1
            if len(source) <= 1:
                break

            current_time = self[index].value
            if source[0].value < current_time:
                self.insert(index, source.pop(0))
            elif source[0].value == current_time:
                del source[0]
            index += 1

        if len(source) > 0:
            del self[-1]
        while len(source) > 0:
            self.append(source.pop(0))

    def removeAllEventsOfType(self, event_type):
        index = 0
        while index < len(self):
            if isinstance(self[index], event_type):
                del self[index]
            else:
                index += 1

    def removeNullDeltaTimeEvents(self):
        for i, event in enumerate(self):
            if isinstance(event, TimeEvent) and event.value == 0:
                del self[i]

    def updateChannelSet(self, new_event):
        if isinstance(new_event, ChannelEvent):
            self.channels.add(new_event.channel_index)

    def __str__(self):
        string_to_print = f"Track Number: {self.track_number}\nTicks Per Beat: {self.ticks_per_beat}\n"
        for event in self:
            string_to_print += event.__str__()

        return string_to_print

class Event:
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return f"Generic Event:\n    {self.message}\n"

class ChannelEvent(Event):
    def __init__(self, channel_index):
        self.channel_index = channel_index

    def __str__(self):
            return f"Channel Event:\n    Channel Number: {self.channel_index}\n"

class ControlChangeEvent(ChannelEvent):
    def __init__(self, channel_index, control_number, value):
        super().__init__(channel_index)
        self.control_number = control_number
        self.value = value

    def __str__(self):
        string_to_print = f"Control Change:\n    Channel Number: {self.channel_index}\n    Control Number: {self.control_number}\n    Value: {self.value}\n"

        return string_to_print

class KeySignatureEvent(Event):
    def __init__(self, number_accidentals, is_minor=False):
        self.number_accidentals = number_accidentals
        self.is_minor = is_minor

    def __str__(self):
        string_to_print = f"Key Signature:\n    Number of Accidentals: {self.number_accidentals}\n    Is Minor: {self.is_minor}\n"

        return string_to_print

class MidiPortEvent(Event):
    def __init__(self, port):
        self.port = port

    def __str__(self):
        string_to_print = f"Midi Port:\n    Port Number: {self.port}\n"

        return string_to_print

class NoteOnEvent(ChannelEvent):
    def __init__(self, channel_index, note_number, velocity):
        super().__init__(channel_index)
        self.note_number = note_number
        self.velocity = velocity

    def __str__(self):
        string_to_print = f"Note On:\n    Channel Number: {self.channel_index}\n    Note Number: {self.note_number} ({convertMidiToPitchNotation(self.note_number)})\n    Velocity: {self.velocity}\n"

        return string_to_print

class NoteOffEvent(ChannelEvent):
    def __init__(self, channel_index, note_number, velocity):
        super().__init__(channel_index)
        self.note_number = note_number
        self.velocity = velocity

    def __str__(self):
        string_to_print = f"Note Off:\n    Channel Number: {self.channel_index}\n    Note Number: {self.note_number}\n    Velocity: {self.velocity}\n"

        return string_to_print

class ProgramChangeEvent(ChannelEvent):
    def __init__(self, channel_index, program_number):
        super().__init__(channel_index)
        self.program_number = program_number

    def __str__(self):
        string_to_print = f"Program Change:\n    Channel Number: {self.channel_index}\n    Program Number: {self.program_number}\n"

        return string_to_print

class TempoEvent(Event):
    def __init__(self, microseconds_per_beat):
        self.microseconds_per_beat = microseconds_per_beat

    def __str__(self):
        string_to_print = f"Tempo:\n    Microseconds/Beat: {self.microseconds_per_beat}\n"

        return string_to_print

class TimeEvent(Event):
    def __init__(self, value, time_event_type=TimeEventType.DELTA):
        self.value = value
        self.time_event_type = time_event_type

    def __str__(self):
        string_to_print = f"Time:\n    Value: {self.value}\n    Type: {self.time_event_type.value}\n"

        return string_to_print

class TimeSignatureEvent(Event):
    def __init__(self, numerator, denominator):
        self.numerator = numerator
        self.denominator = denominator

    def __str__(self):
        string_to_print = f"Time Signature:\n    Numerator: {self.numerator}\n    Denominator: {self.denominator}\n"

        return string_to_print

class TrackEndEvent(Event):
    def __init__(self):
        pass

    def __str__(self):
        string_to_print = f"Track End\n"

        return string_to_print

class TrackNameEvent(Event):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        string_to_print = f"Track Name:\n    {self.name}\n"

        return string_to_print