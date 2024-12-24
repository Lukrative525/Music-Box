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

