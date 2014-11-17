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
    
    #Menu Actions
    ibuilder_new_project = QtCore.pyqtSignal(name = "ibuilder_new_project")

    #IBuilder Actions
    project_tree_refresh = QtCore.pyqtSignal(name = "refresh_project")
    project_tree_clear_signal = QtCore.pyqtSignal(name = "project_tree_clear")
    project_tree_changed_signal = QtCore.pyqtSignal(object, object, object, name = "project_tree_changed")
    project_tree_get_first_dev = QtCore.pyqtSignal(name = "project_tree_first_dev")

    module_selected = QtCore.pyqtSignal(str, name = "ibuilder_module_selected")
    module_deselected = QtCore.pyqtSignal(str, name = "ibuilder_module_deselected")

    slave_selected = QtCore.pyqtSignal(str, str, name = "ibuilder_slave_selected")
    slave_deselected = QtCore.pyqtSignal(str, str, name = "ibuilder_slave_deselected")

    remove_tab = QtCore.pyqtSignal(object, name = "ibuilder_remove_tab")

