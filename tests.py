from midi_elements import *

track = Track(1)
event1 = NoteStart(60)
event2 = TimeDelta(1)
event3 = NoteEnd(60)

track.append(event1)
track.append(event2)
track.append(event3)

print(track)

track.append(TimeSignature(4, 4))
track.append(KeySignature(2))

print(track)

track.append(TrackEnd())
track.append(Event())

print(track)
