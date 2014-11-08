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

    #Nysa GUI Actions
    show_host_view = QtCore.pyqtSignal(name = "show_host_view")
    show_ibuilder_view = QtCore.pyqtSignal(name = "show_ibuilder_view")
    show_cbuilder_view = QtCore.pyqtSignal(name = "show_cbuilder_view")

