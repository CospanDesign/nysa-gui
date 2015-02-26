import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

_gpio_action_instance = None

#Singleton Magic
def RegisterViewerActions(*args, **kw):
    global _gpio_action_instance
    if _gpio_action_instance is None:
        _gpio_action_instance = _RegisterViewerActions(*args, **kw)
    return _gpio_action_instance

class _RegisterViewerActions(QtCore.QObject):

    #Raw Register signals
    get_pressed = QtCore.pyqtSignal(int, name = "get_pressed")
    set_pressed = QtCore.pyqtSignal(int, int, name = "set_pressed")

