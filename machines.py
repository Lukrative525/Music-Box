from machine_components.printer_components import Printer, AxisType

printer_of_theseus = Printer()
printer_of_theseus.addAxis("X", AxisType.LINEAR, 118, -118, 7527, 0, 6.25, 16)
printer_of_theseus.addAxis("Y", AxisType.LINEAR, 100, -100, 7527, 0, 6.25, 16)
printer_of_theseus.addAxis("Z", AxisType.LINEAR, 190, 10, 941, 100, 25, 16)
printer_of_theseus.addAxis("A", AxisType.ROTARY, 190, -190, 4704, 0, 10, 16)
printer_of_theseus.addAxis("B", AxisType.ROTARY, 190, -190, 4704, 0, 10, 16)
printer_of_theseus.setTimeKeeper("E", -30, 0)

ender_3 = Printer()
ender_3.addAxis("X", AxisType.LINEAR, 210, 10, 12000, 110, 5, 16)
ender_3.addAxis("Y", AxisType.LINEAR, 210, 10, 12000, 110, 5, 16)
ender_3.addAxis("Z", AxisType.LINEAR, 240, 10, 600, 125, 25, 16)
ender_3.setTimeKeeper("E", -30, 0)