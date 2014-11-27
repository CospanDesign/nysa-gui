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

    #Bind events
    internal_bind_disconnect = QtCore.pyqtSignal(str, name = "ibuilder_configuration_ib_disc")
    internal_bind_connect = QtCore.pyqtSignal(str, str, name = "ibuilder_configuration_ib_conn")

    #Configuration options
    update_project_name = QtCore.pyqtSignal(str, str, name = "ibuilder_configuration_update_name")
    update_board = QtCore.pyqtSignal(str, name = "ibuilder_configuration_update_board")

    add_constraint_file = QtCore.pyqtSignal(str, name = "ibuilder_configuration_add_const")
    remove_constraint_file = QtCore.pyqtSignal(str, name = "ibuilder_configuration_remove_const")
    add_default_board_constraint = QtCore.pyqtSignal(name = "ibuilder_add_default_board_const")
    remove_default_board_constraint = QtCore.pyqtSignal(name = "ibuilder_remove_default_board_const")

    #Slave Parameters
    commit_slave_parameters = QtCore.pyqtSignal(str, object, name = "ibuilder_designer_commit_slave_params")
