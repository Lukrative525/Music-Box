from midi_elements import *

track = Track(0)
event1 = NoteOnEvent(0, 60, 80)
event3 = NoteOnEvent(0, 60, 0)

track.append(event1)
track.append(event3)

track.append(TimeSignatureEvent(4, 4))
track.append(KeySignatureEvent(2))

track.append(TrackEndEvent())
track.append(Event())

print(track)
