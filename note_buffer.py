class Note:
    def __init__(self, note_number=None):
        self.note_number = note_number

class Channel(dict[int, Note]):
    def __init__(self):
        super().__init__()

class Segment(dict[int, Channel]):
    def __init__(self, number_channels):
        super().__init__()
        for i in range(number_channels):
            self[i] = Channel()
        self.duration = 0

if __name__ == "__main__":
    segment = Segment(5)
    segment[2] = 