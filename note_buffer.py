from __future__ import annotations
from midi_elements import convertMidiToPitchNotation

class Channel(set):
    def __init__(self):
        super().__init__()

    def add(self, note_number):
        super().add(note_number)

    def getNote(self):
        if not self.isEmpty():
            return min(self)
        else:
            return None

    def isEmpty(self):
        if len(self) == 0:
            return True
        else:
            return False

    def remove(self, note_number):
        super().discard(note_number)

    def __str__(self):
        string = "Empty"
        for note_number in sorted(self, reverse=True):
            string = str(convertMidiToPitchNotation(note_number))

        return string

class NoteBuffer:
    def __init__(self, channel_indices: set):
        self.channels: dict[int, Channel] = {}
        for channel_index in channel_indices:
            self.channels[channel_index] = Channel()
        self.channel_indices = channel_indices
        self.duration = 0

    def copyNotes(self, source_buffer: NoteBuffer):
        if not source_buffer.channel_indices == self.channel_indices:
            raise Exception("Source buffer must have the same channel indices to copy.")

        for channel_index in self.channel_indices:
            self.channels[channel_index].clear()
            for note_number in source_buffer.channels[channel_index]:
                self.channels[channel_index].add(note_number)

        self.duration = source_buffer.duration

    def __str__(self):
        string = f"{round(self.duration, 3)}: "
        for index, channel in self.channels.items():
            string += (channel.__str__() + ", ")
        string = string[:-2]

        return string