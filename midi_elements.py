class Track(list):
    def __init__(self, track_number):
        self.track_number = track_number

    def append(self, new_event):
        if isinstance(new_event, Event) and not any(isinstance(event, TrackEndEvent) for event in self):
            super().append(new_event)

    def convertNullNoteOnToNoteOff(self):
        for i, event in enumerate(self):
            if isinstance(event, NoteOnEvent) and event.velocity == 0:
                self[i] = NoteOffEvent(event.channel_number, event.note_number, event.velocity)

    def convertDeltaTimeToElapsedTime(self):
        current_time = 0
        for event in self:
            if isinstance(event, TimeEvent):
                event.time += current_time
                current_time = event.time

    def __str__(self):
        string_to_print = f"Track Number: {self.track_number}\n"
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
        string_to_print = f"Key Signature:\n    Number Accidentals: {self.number_accidentals}\n    Is Minor: {self.is_minor}\n"

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
    def __init__(self, time):
        super().__init__()
        self.time = time

    def __str__(self):
        string_to_print = f"Time: {self.time}\n"

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