from __future__ import annotations

class Channel(set):
    def __init__(self):
        super().__init__()

    def add(self, note_number):
        super().add(note_number)

    def remove(self, note_number):
        super().discard(note_number)

class NoteBuffer:
    def __init__(self, number_channels):
        self.channels: dict[int, Channel] = {}
        for i in range(number_channels):
            self.channels[i] = Channel()
        self.duration = 0

    def copyNotes(self, source_buffer: NoteBuffer):
        if not len(source_buffer.channels) == len(self.channels):
            raise Exception("Source buffer must have the same number of channels to copy")

        for channel_number in range(len(self.channels)):
            self.channels[channel_number].clear()
            for note_number in source_buffer.channels[channel_number]:
                self.channels[channel_number].add(note_number)

        self.duration = source_buffer.duration