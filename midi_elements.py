class Track(list):
    def __init__(self, channel_number):
        self.channel_number = channel_number

    def append(self, event):
        if isinstance(event, Event) and not any(isinstance(event, TrackEnd) for event in self):
            super().append(event)

    def __str__(self):
        string_to_print = f"Channel Number: {self.channel_number}\n"
        for event in self:
            string_to_print += event.__str__()

        return string_to_print

class Event:
    def __init__(self):
        pass

    def __str__(self):
        return f"Generic Event at {hex(id(self))}\n"

class KeySignature(Event):
    def __init__(self, number_accidentals, is_minor=False):
        super().__init__()
        self.number_accidentals = number_accidentals
        self.is_minor = is_minor

    def __str__(self):
        string_to_print = f"Key Signature Change:\n    Number Accidentals: {self.number_accidentals}\n    Is Minor: {self.is_minor}\n"

        return string_to_print

class NoteStart(Event):
    def __init__(self, note_value):
        super().__init__()
        self.note_value = note_value

    def __str__(self):
        string_to_print = f"Note Start: {self.note_value}\n"

        return string_to_print

class NoteEnd(Event):
    def __init__(self, note_value):
        super().__init__()
        self.note_value = note_value

    def __str__(self):
        string_to_print = f"Note End: {self.note_value}\n"

        return string_to_print

class Tempo(Event):
    def __init__(self, tempo):
        super().__init__()
        self.tempo = tempo

    def __str__(self):
        string_to_print = f"Tempo: {self.tempo}\n"

        return string_to_print

class TimeDelta(Event):
    def __init__(self, time_value):
        super().__init__()
        self.time_value = time_value

    def __str__(self):
        string_to_print = f"Time Delta: {self.time_value}\n"

        return string_to_print

class TimeSignature(Event):
    def __init__(self, numerator, denominator):
        super().__init__()
        self.numerator = numerator
        self.denominator = denominator

    def __str__(self):
        string_to_print = f"Time Signature Change:\n    Numerator: {self.numerator}\n    Denominator: {self.denominator}\n"

        return string_to_print

class TrackEnd(Event):
    def __init__(self):
        super().__init__()

    def __str__(self):
        string_to_print = f"Track End\n"

        return string_to_print