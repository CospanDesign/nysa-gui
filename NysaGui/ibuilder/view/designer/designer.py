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

from defines import PERIPHERAL_BUS_COLOR
from defines import MEMORY_BUS_COLOR

class Designer(QWidget):
    def __init__(self, actions, status):
        super (Designer, self).__init__()
        self.status = status
        self.actions = actions
        self.nbv = NysaBusView(self, actions, status)

        layout = QHBoxLayout()
        box_layout = QVBoxLayout()
        layout.addWidget(self.nbv)
        #self.peripheral_slave_box = BoxList(color = PERIPHERAL_BUS_COLOR)
        self.peripheral_slave_box = BoxList(color = "blue")
        #self.memory_slave_box = BoxList(color = MEMORY_BUS_COLOR)
        self.memory_slave_box = BoxList(color = "purple")
        box_layout.addWidget(self.peripheral_slave_box)
        box_layout.addWidget(self.memory_slave_box)
        layout.addLayout(box_layout)
        self.setLayout(layout)
        self.actions.setup_peripheral_bus_list.connect(self.setup_peripheral_slave_list)
        self.actions.setup_memory_bus_list.connect(self.setup_memory_slave_list)

    def set_controller(self, controller):
        self.nbv.set_controller(controller)

    def get_scene(self):
        return self.nbv.get_scene()

    def setup_peripheral_slave_list(self, peripheral_dict):
        #print "peripheral_dict: %s" % str(peripheral_dict.keys())
        self.peripheral_slave_box.add_items(peripheral_dict, "peripheral_slave")

    def setup_memory_slave_list(self, memory_dict):
        self.memory_slave_box.add_items(memory_dict, "memory_slave")

