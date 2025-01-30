Music-Box is an application for converting MIDI files into musical G-code readable by FDM 3D printers. If its stepper motors are noisy enough, the 3D printer will playback the music from the original MIDI file when the G-code file is run.

See this in action: [https://youtu.be/1bL-VmJUtvs](https://youtu.be/1bL-VmJUtvs)

# Environment Setup

Make sure to set your working directory to the one containing this project.

# Creating a Machine Definition

The generated G-code is tailored to the specifications of the machine doing the playback, so to use this application, you must first define your printer as a `Printer` object. Here is an example of how to do this, taken from `machines.py`:

```
from machine_elements.printer_components import Printer, AxisType

printer_of_theseus = Printer()
printer_of_theseus.addAxis("X", AxisType.LINEAR, 118, -118, 7527, 0, 6.25, 16)
printer_of_theseus.addAxis("Y", AxisType.LINEAR, 100, -100, 7527, 0, 6.25, 16)
printer_of_theseus.addAxis("Z", AxisType.LINEAR, 190, 10, 941, 100, 25, 16)
printer_of_theseus.addAxis("A", AxisType.ROTARY, 190, -190, 4704, 0, 10, 16)
printer_of_theseus.addAxis("B", AxisType.ROTARY, 190, -190, 4704, 0, 10, 16)
printer_of_theseus.setTimeKeeper("E", -30, 0)
printer_of_theseus.setPrecision(5)
```

The `addAxis` method of the `Printer` class takes the following parameters: `label`, `axis_type`, `upper_limit`, `lower_limit`, `max_feed_rate`, `starting_position`, `base_steps_per_millimeter`, and `microstepping_factor`.

The `setTimeKeeper` method defines the axis used to keep all of the others in sync. It doesn't play any notes, but rather rotates slowly at a constant rate during the entirety of the G-code file execution. Using an axis in this way, rather than using `G4` dwell commands, makes the rythms more accurate. The parameters for this command are: `label`, `feed_rate`, and `starting_position`. It is most common to use the extruder axis for this, and to choose a negative feedrate so that if you forget to remove the filament from the hotend, it (hopefully) simply removes it on its own.

`setPrecision` sets the number of decimal places to dislay in the generated G-code.

Once you have finished defining your machine, you can import it into other files where needed.

# Using the Application

With a machine defined, you can now use it in `music_box_printer.py`. Simply replace the machine used by default with the one you defined:

```diff
- generator = PrinterGcodeGenerator(machines.printer_of_theseus)
+ generator = PrinterGcodeGenerator(machines.your_new_machine)
```

Run `music_box_printer.py` and, using the file open dialog that appears, select the MIDI files you want to convert into G-code. The selected files will not be modified: instead, corresponding G-code files with the same name will be created in the same directory as the MIDI files.
