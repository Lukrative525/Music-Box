from settings_printer import Printer

printer_of_theseus = Printer()
printer_of_theseus.addAxis("X", Printer.Axis.AxisType.LINEAR, 118, -118, 7527, 0, 6.25, 16)
printer_of_theseus.addAxis("Y", Printer.Axis.AxisType.LINEAR, 100, -100, 7527, 0, 6.25, 16)
printer_of_theseus.addAxis("Z", Printer.Axis.AxisType.LINEAR, 190, 10, 941, 100, 25, 16)
printer_of_theseus.addAxis("A", Printer.Axis.AxisType.ROTARY, 190, -190, 4704, 0, 10, 16)
printer_of_theseus.addAxis("B", Printer.Axis.AxisType.ROTARY, 190, -190, 4704, 0, 10, 16)
printer_of_theseus.setTimeKeeper("E", -30)