import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

class IBuilderProjectActions(QtCore.QObject):
    
    #Menu Actions
    module_selected = QtCore.pyqtSignal(str, name = "ibuilder_project_module_selected")
    module_deselected = QtCore.pyqtSignal(str, name = "ibuilder_project_module_deselected")

    slave_selected = QtCore.pyqtSignal(str, str, name = "ibuilder_project_slave_selected")
    slave_deselected = QtCore.pyqtSignal(str, str, name = "ibuilder_project_slave_deselected")

    #Drag Events
    drop_event = QtCore.pyqtSignal(object, name = "ibuilder_designer_drop_event")
    drag_enter_event = QtCore.pyqtSignal(object , name = "ibuilder_designer_drag_enter_event")
    drag_leave_event = QtCore.pyqtSignal(object , name = "ibuilder_designer_drag_leave_event")
    drag_move_event = QtCore.pyqtSignal(object, name = "ibuilder_designer_drag_move_event")

    setup_peripheral_bus_list= QtCore.pyqtSignal(object, name = "ibuilder_designer_setup_plist")
    setup_memory_bus_list= QtCore.pyqtSignal(object, name = "ibuilder_designer_setup_mlist")

    remove_slave = QtCore.pyqtSignal(str, int, name = "ibuilder_designer_remove_slave")