from __future__ import annotations
from enum import Enum

class TimeEventType(Enum):
    DELTA = "delta"
    ELAPSED = "elapsed"

class Track(list):
    def __init__(self, track_number, ticks_per_beat):
        self.track_number = track_number
        self.ticks_per_beat = ticks_per_beat

    def append(self, new_event):
        if isinstance(new_event, Event) and not any(isinstance(event, TrackEndEvent) for event in self):
            super().append(new_event)

    def convertDeltaTimeToElapsedTime(self):
        if not self.hasOnlyTimeEventsOfType(TimeEventType.DELTA):
            raise Exception(f"Cannot perform time event conversion to type \"{TimeEventType.ELAPSED.value}\": track already contains time events of this type")
        elapsed_time = 0
        for event in self:
            if isinstance(event, TimeEvent):
                elapsed_time = event.value + elapsed_time
                event.value = elapsed_time
                event.time_event_type = TimeEventType.ELAPSED

    def convertElapsedTimeToDeltaTime(self):
        if not self.hasOnlyTimeEventsOfType(TimeEventType.ELAPSED):
            raise Exception(f"Cannot perform time event conversion to type \"{TimeEventType.DELTA.value}\": track already contains time events of this type")
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
                self[i] = NoteOffEvent(event.channel_number, event.note_number, event.velocity)

    def hasOnlyTimeEventsOfType(self, desired_type=TimeEventType.DELTA):
        has_only_time_events_of_type = True
        for event in self:
            if isinstance(event, TimeEvent):
                if not event.time_event_type == desired_type:
                    has_only_time_events_of_type = False

        return has_only_time_events_of_type

    def mergeTracks(self, source: Track):

        if not self.hasOnlyTimeEventsOfType(TimeEventType.ELAPSED) or not source.hasOnlyTimeEventsOfType(TimeEventType.ELAPSED):
            raise Exception(f"To perform a track merge, both tracks must have only time events of type \"{TimeEventType.ELAPSED.value}\"")

        if not isinstance(self[-1], TrackEndEvent):
            raise Exception("Target track for merge is missing a track end event")
        elif not isinstance(source[-1], TrackEndEvent):
            raise Exception("Source track for merge is missing a track end event")

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
            elif source[0].value > current_time:
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

class ControlChangeEvent(Event):
    def __init__(self, channel_number, control_number, value):
        super().__init__()
        self.channel_number = channel_number
        self.control_number = control_number
        self.value = value

    def __str__(self):
        string_to_print = f"Control Change:\n    Channel Number: {self.channel_number}\n    Control Number: {self.control_number}\n    Value: {self.value}\n"

        return string_to_print

class KeySignatureEvent(Event):
    def __init__(self, number_accidentals, is_minor=False):
        super().__init__()
        self.number_accidentals = number_accidentals
        self.is_minor = is_minor

    def __str__(self):
        string_to_print = f"Key Signature:\n    Number of Accidentals: {self.number_accidentals}\n    Is Minor: {self.is_minor}\n"

        return string_to_print

class MidiPortEvent(Event):
    def __init__(self, port):
        super().__init__()
        self.port = port

    def __str__(self):
        string_to_print = f"Midi Port:\n    Port Number: {self.port}\n"

        return string_to_print

class NoteOnEvent(Event):
    def __init__(self, channel_number, note_number, velocity):
        super().__init__()
        self.channel_number = channel_number
        self.note_number = note_number
        self.velocity = velocity

    def __str__(self):
        string_to_print = f"Note On:\n    Channel Number: {self.channel_number}\n    Note Number: {self.note_number}\n    Velocity: {self.velocity}\n"

        return string_to_print

class NoteOffEvent(Event):
    def __init__(self, channel_number, note_number, velocity):
        super().__init__()
        self.channel_number = channel_number
        self.note_number = note_number
        self.velocity = velocity

    def __str__(self):
        string_to_print = f"Note Off:\n    Channel Number: {self.channel_number}\n    Note Number: {self.note_number}\n    Velocity: {self.velocity}\n"

        return string_to_print

class ProgramChangeEvent(Event):
    def __init__(self, channel_number, program_number):
        super().__init__()
        self.channel_number = channel_number
        self.program_number = program_number

    def __str__(self):
        string_to_print = f"Program Change:\n    Channel Number: {self.channel_number}\n    Program Number: {self.program_number}\n"

        return string_to_print

class TempoEvent(Event):
    def __init__(self, microseconds_per_beat):
        super().__init__()
        self.microseconds_per_beat = microseconds_per_beat

    def __str__(self):
        string_to_print = f"Tempo:\n    Microseconds/Beat: {self.microseconds_per_beat}\n"

        return string_to_print

class TimeEvent(Event):
    def __init__(self, value, time_event_type=TimeEventType.DELTA):
        super().__init__()
        self.value = value
        self.time_event_type = time_event_type

    def __str__(self):
        string_to_print = f"Time:\n    Value: {self.value}\n    Type: {self.time_event_type.value}\n"

        return string_to_print

class TimeSignatureEvent(Event):
    def __init__(self, numerator, denominator):
        super().__init__()
        self.numerator = numerator
        self.denominator = denominator

    def __str__(self):
        string_to_print = f"Time Signature:\n    Numerator: {self.numerator}\n    Denominator: {self.denominator}\n"

        return string_to_print

class TrackEndEvent(Event):
    def __init__(self):
        super().__init__()

    def __str__(self):
        string_to_print = f"Track End\n"

        return string_to_print

class TrackNameEvent(Event):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __str__(self):
        string_to_print = f"Track Name:\n    {self.name}\n"

        return string_to_print