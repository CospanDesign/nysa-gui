# Copyright (c) 2014 Dave McCoy (dave.mccoy@cospandesign.com)

# This file is part of Nysa (wiki.cospandesign.com/index.php?title=Nysa).
#
# Nysa is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# Nysa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Nysa; If not, see <http://www.gnu.org/licenses/>.


__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from functools import partial

sys.path.append(os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              "common",
                              "pvg"))

sys.path.append(os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              "common",
                              "nysa_bus_view"))

#from visual_graph.box import Box
#from box_list import BoxList
from nysa_bus_view import NysaBusView
from box_list import BoxList
from integration_dialog import IntegrationDialog

from defines import PERIPHERAL_BUS_COLOR
from defines import MEMORY_BUS_COLOR


NO_MODULE_SEL = "No Module Selected"

class Designer(QWidget):
    def __init__(self, actions, status):
        super (Designer, self).__init__()
        self.status = status
        self.actions = actions
        self.nbv = NysaBusView(self, actions, status)
        self.parameter_table = self.create_parameters_table()

        layout = QHBoxLayout()
        control_layout = QVBoxLayout()
        layout.addWidget(self.nbv)
        #self.peripheral_slave_box = BoxList(color = PERIPHERAL_BUS_COLOR)
        self.peripheral_slave_box = BoxList(color = "blue")
        #self.memory_slave_box = BoxList(color = MEMORY_BUS_COLOR)
        self.memory_slave_box = BoxList(color = "purple")
        control_layout.addWidget(self.peripheral_slave_box)
        control_layout.addWidget(self.memory_slave_box)
        control_layout.addWidget(self.parameter_table)
        layout.addLayout(control_layout)
        self.setLayout(layout)
        self.actions.setup_peripheral_bus_list.connect(self.setup_peripheral_slave_list)
        self.actions.setup_memory_bus_list.connect(self.setup_memory_slave_list)
        self.actions.module_selected.connect(self.module_selected)
        self.actions.module_deselected.connect(self.module_deselected)
        self.actions.slave_selected.connect(self.slave_selected)
        self.actions.slave_deselected.connect(self.slave_deselected)
        self.controller = None
        self.user_signal = None

    def set_controller(self, controller):
        self.nbv.set_controller(controller)
        self.controller = controller

    def get_scene(self):
        return self.nbv.get_scene()

    def setup_peripheral_slave_list(self, peripheral_dict):
        #print "peripheral_dict: %s" % str(peripheral_dict.keys())
        self.peripheral_slave_box.add_items(peripheral_dict, "peripheral_slave")

    def setup_memory_slave_list(self, memory_dict):
        self.memory_slave_box.add_items(memory_dict, "memory_slave")

    def module_selected(self, module):
        #print "%s selected" % module
        self.clear_param_table()
        self.populate_param_table(module, parameters = None)

    def module_deselected(self, module):
        #print "%s deselected" % module
        self.clear_param_table()

    def slave_selected(self, slave_name, bus_name):
        #print "%s-%s selected" % (bus_name, slave_name)
        parameters = {}
        if str(slave_name).lower() == "sdb":
            self.clear_param_table()
            self.populate_param_table(slave_name, parameters)
            return

        tags = self.controller.get_slave_tags(bus_name, slave_name)

        model = self.controller.get_model()
        project_tags = self.controller.get_module_project_tags(slave_name)

        pfound = False
        if "parameters" in tags:
            for parameter in tags["parameters"]:
                if "parameters" in project_tags:
                    pfound = False
                    for pparameter in project_tags["parameters"]:
                        if pparameter == parameter:
                            #print "pparameter: %s" % pparameter
                            #print "parameter: %s" % parameter
                            parameters[parameter] = project_tags["parameters"][pparameter]
                            pfound = True
                            break
                if not pfound:
                    parameters[parameter] = tags["parameters"][parameter]

        self.clear_param_table()
        self.populate_param_table(slave_name, parameters)
        #print "bus name: %s" % bus_name
        if bus_name.toLower() == "peripherals":
            bn = str(bus_name)
            self.integration_button.setEnabled(True)
            integration_list = []
            if "integration" in project_tags:
                integration_list = project_tags["integration"]
        
            full_list = []
            for slave_index in range(model.get_number_of_peripheral_slaves()):
                name = model.get_slave_name(bn, slave_index)
                if name == slave_name:
                    continue

                full_list.append(name)
            f = partial(self.update_integration,
                        bn,
                        slave_name,
                        integration_list,
                        full_list)
            self.user_signal = f
            #print "signal: %s" % str(dir(self.integration_button.clicked))

            self.integration_button.clicked.connect(f)
            self.integration_button.setEnabled(True)

        #Does this slave have a arbiter master?
        self.slave_id_line.setDisabled(False)

    def slave_deselected(self, slave_name, bus_name):
        #print "%s-%s deselected" % (bus_name, slave_name)
        self.clear_param_table()

    def populate_param_table(self, name, parameters):
        #print "Populating Parameter Table"
        #print "Module tags: %s" % str(tags)
        self.sel_slave_name.setText(name)
        #print "Adding integration Record Dialog"
        if parameters is None:
            return

        count = len(parameters)
        if count == 0:
            return

        self.param_table.setRowCount(count)
        for parameter in parameters:
            i = parameters.keys().index(parameter)
            self.param_table.setCellWidget(i, 0, QLabel(parameter))
            self.param_table.setCellWidget(i, 1, QLineEdit(parameters[parameter]))

        self.param_table.resizeColumnsToContents()
        self.commit_params_button.setEnabled(True)

    def create_parameters_table(self):
        pt = QWidget(self)
        pt.setMaximumWidth(300)

        self.slave_id_line = QLineEdit("")
        v = QIntValidator()
        v.setBottom(0)
        v.setTop(256)
        self.slave_id_line.setValidator(v)
        self.slave_id_line.setDisabled(True)

        self.sel_slave_name = QLabel(NO_MODULE_SEL)
        layout = QVBoxLayout()

        #Add Integration Dialog Button
        self.integration_button = QPushButton("Modify Component Integration")
        self.integration_button.setDisabled(True)

        layout.addWidget(self.sel_slave_name)
        layout.addWidget(self.integration_button)

        self.param_table = QTableWidget()
        self.param_table.setColumnCount(2)
        self.param_table.setRowCount(1)
        self.param_table.setHorizontalHeaderLabels(["Name", "Value"])
        self.param_table.horizontalHeader().setStretchLastSection(True)

        self.commit_params_button = QPushButton("Commit Parameters")
        self.commit_params_button.setDisabled(True)
        self.commit_params_button.clicked.connect(self.commit_parameters_clicked)

        layout.addWidget(self.param_table)
        layout.addWidget(self.commit_params_button)
        pt.setLayout(layout)
        return pt

    def commit_parameters_clicked(self):
        #self.actions.slave_parameters_clicked
        name = self.sel_slave_name.text()
        param_count = self.param_table.rowCount()
        if param_count == 0:
            return

        param_dict = {}
        for i in range(param_count):
            param_dict[self.param_table.cellWidget(i, 0).text()] = self.param_table.cellWidget(i, 1).text()
        self.actions.commit_slave_parameters.emit(name, param_dict)

    def clear_param_table(self):
        self.sel_slave_name.setText(NO_MODULE_SEL)
        self.slave_id_line.setText("")
        self.slave_id_line.setDisabled(True)
        self.param_table.clear()
        self.param_table.setRowCount(0)
        self.param_table.setHorizontalHeaderLabels(["Name", "Value"])
        self.commit_params_button.setDisabled(True)
        self.integration_button.setDisabled(True)

        if self.user_signal is not None:
            self.integration_button.clicked.disconnect(self.user_signal)
            self.user_signal = None

    def update_integration(self, bus_name, name, connected_components, all_components):
        connected_components = IntegrationDialog.get_integration_list(name, all_components, connected_components)
        #print "Update integration: %s, %s, %s" % (name, connected_components, all_components)
        tags = self.controller.get_slave_tags(bus_name, name)
        tags["integration"] = connected_components
        self.actions.commit_slave_integration_list.emit(bus_name, name, connected_components)



