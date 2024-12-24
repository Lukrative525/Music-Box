import gcode_generation as gg
import machines
import midi_parsing as mp
from tkinter import filedialog, Tk

root = Tk()
root.withdraw()
file_names: str = filedialog.askopenfilename(filetypes = [('MIDI files','*.mid')], multiple = True)
file_names = list(file_names)

# strip .mid from full file path to replace later with .gcode
for i in range(len(file_names)):
    if '.mid' not in file_names[i]:
        raise Exception('Please select a MIDI file')
    file_names[i] = file_names[i].replace('.mid', '')

# strip file path from file names to print to console (better readability)
short_file_names = file_names[:]
for i in range(len(short_file_names)):
    while '/' in short_file_names[i]:
        short_file_names[i] = short_file_names[i][(short_file_names[i].find('/') + 1):]

# use midi files for generation of musical gcode
source_files = file_names[:]
target_files = file_names[:]
for i in range(len(file_names)):
    source_files[i] = file_names[i] + '.mid'
    target_files[i] = file_names[i] + '.gcode'

# generate gcode files
print()
for short_file_name, source_file, target_file in zip(short_file_names, source_files, target_files):
    print(f'{short_file_name}\n')
    tracks = mp.parseMidiFile(source_file)
    condensed_track = mp.condenseMidiTracks(tracks)
    condensed_track.convertElapsedTimeToDeltaTime()
    condensed_track.convertTicksToMicroseconds()
    gg.generatePrinterGcode(target_file, condensed_track, machines.printer_of_theseus)
print('Finished\n')