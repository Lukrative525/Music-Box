# calculate the max feeds for highest midi notes of each axis

import gcode_maker as gm
import numpy as np

settings = gm.get_printer_settings()

midi = 108
feeds_max = np.zeros(len(settings[0]))
frequency_max = gm.calculate_frequency(midi)

for j in range(len(settings[0])):
    feeds_max[j] = (frequency_max * 60) / settings[1][j]

double_max = np.ceil(2 * feeds_max)
feeds_max = np.ceil(feeds_max)

print(feeds_max)
print(double_max)
print(frequency_max)