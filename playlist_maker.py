import numpy as np
import random
import tkinter as tk
from tkinter import filedialog

SHUFFLE = True

tk.Tk().withdraw()
file_names = filedialog.askopenfilename(filetypes = [('Gcode files','*.gcode')], multiple = True)
file_names = list(file_names)

# strip file path from file names
printer_file_names = file_names[:]
for i in range(len(file_names)):
    while '/' in printer_file_names[i]:
        printer_file_names[i] = printer_file_names[i][(printer_file_names[i].find('/') + 1):]

# this is the file path to the music file on the printer's SD card
printer_file_path = '0:/macros/Music Box/Music Files/'

# this is the complete file path to the playlist file on the computer
playlist_file_path = 'C:/Users/Luke/Documents/3D printing/music box/Playlist.gcode'

# add the file path to the music files on the printer's SD card to the file names
for i in range(len(file_names)):
    printer_file_names[i] = printer_file_path + printer_file_names[i]

# create indices to shuffle and use if SHUFFLE is True, and to use as is if it's False
indices = np.arange(0, len(file_names))
if SHUFFLE == True:
    random.shuffle(indices)
print(f'\n{indices}\n')

# write out gcode commands
playlist = open(playlist_file_path, 'w')

playlist.write('echo "Trip blob detector to stop loop"')
playlist.write('\nset global.stop_music = false')
playlist.write('\nwhile global.stop_music == false')

for i in indices:
    playlist.write('\n\tif global.stop_music == false')
    playlist.write(f'\n\t\tM98 P"{printer_file_names[i]}"')

playlist.close