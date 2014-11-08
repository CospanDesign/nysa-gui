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

    #Host Actions
    #Control Signals
    add_device_signal = QtCore.pyqtSignal(str, str, object, name = "add_device")
    remove_device_signal = QtCore.pyqtSignal(str, str, name = "remove_device")

    #View Signals
    platform_tree_refresh = QtCore.pyqtSignal(name = "refresh_platform")
    platform_tree_clear_signal = QtCore.pyqtSignal(name = "platform_tree_clear")
    platform_tree_changed_signal = QtCore.pyqtSignal(object, object, object, name = "platform_tree_changed")
    platform_tree_get_first_dev = QtCore.pyqtSignal(name = "platform_tree_first_dev")

    host_module_selected = QtCore.pyqtSignal(str, name = "host_module_selected")
    host_module_deselected = QtCore.pyqtSignal(str, name = "host_module_deselected")

    slave_selected = QtCore.pyqtSignal(str, str, name = "host_slave_selected")
    slave_deselected = QtCore.pyqtSignal(str, str, name = "host_slave_deselected")

    script_item_selected = QtCore.pyqtSignal(str, object, name = "host_script_item_selected")
    remove_tab = QtCore.pyqtSignal(object, name = "host_remove_tab")

