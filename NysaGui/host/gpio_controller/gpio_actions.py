import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

class GPIOActions(QtCore.QObject):

    #Raw Register signals
    get_pressed = QtCore.pyqtSignal(int, name = "get_pressed")
    set_pressed = QtCore.pyqtSignal(int, int, name = "set_pressed")

    read_rate_change = QtCore.pyqtSignal(int, name = "read_rate_change")
    read_start_stop = QtCore.pyqtSignal(bool, float, name = "read_start_stop")

    #GPIO Specific signals
    gpio_input_changed = QtCore.pyqtSignal(int, name = "gpio_in_changed")
    gpio_out_changed = QtCore.pyqtSignal(int, bool, name = "gpio_out_changed")
    direction_changed = QtCore.pyqtSignal(int, bool, name = "direction_changed")
    interrupt_en_changed = QtCore.pyqtSignal(int, bool, name = "interrupt_en_changed")
    interrupt_edge_changed = QtCore.pyqtSignal(int, bool, name = "interrupt_edge_changed")
    interrupt_both_edge_changed = QtCore.pyqtSignal(int, bool, name = "interrupt_both_edge_changed")

    gpio_interrupt = QtCore.pyqtSignal(name = "gpio_interrupt")

