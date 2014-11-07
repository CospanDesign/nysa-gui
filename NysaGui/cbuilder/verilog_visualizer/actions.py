import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

_action_instance = None

#Singleton Magic
def Actions(*args, **kw):
    global _action_instance
    if _action_instance is None:
        _action_instance = _Actions(*args, **kw)
    return _action_instance

class _Actions(QtCore.QObject):

    #Control Signals
    refresh_signal = QtCore.pyqtSignal(name = "refresh_platform")

    #View Signals
    add_device_signal = QtCore.pyqtSignal(object, name = "add_device")
    clear_platform_tree_signal = QtCore.pyqtSignal(object, name = "clear_platform_tree_signal")
    platform_tree_get_first_dev = QtCore.pyqtSignal(object, name = "platform_tree_get_first_dev")
    platform_tree_changed_signal = QtCore.pyqtSignal(str, object, object, name = "platfrom_tree_changed_signal")

    add_verilog_core = QtCore.pyqtSignal(str, object, name = "add_verilog_core")
    add_image_config = QtCore.pyqtSignal(object, name = "add_image_config")

    #Visualizer
    module_selected = QtCore.pyqtSignal(str, name = "module_selected")
    module_deselected = QtCore.pyqtSignal(str, name = "module_deselected")

    slave_selected = QtCore.pyqtSignal(str, str, name = "slave_selected")
    slave_deselected = QtCore.pyqtSignal(str, str, name = "slave_deselected")


    def __init__(self, parent = None):
        super (_Actions, self).__init__(parent)

