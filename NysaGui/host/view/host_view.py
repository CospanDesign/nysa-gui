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


""" nysa interface
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from gui_utils import get_color_from_id
from platform_tree.platform_tree import PlatformTree

from tab_manager import TabManager

from nysa_bus_view.nysa_bus_view import NysaBusView

class HostView(QWidget):
    def __init__(self, gui_actions, actions, status):
        super (HostView, self).__init__()
        layout = QVBoxLayout()
        self.status = status
        self.gui_actions = gui_actions
        self.actions = actions
        self.menu_actions = []
        self.setObjectName("host")


        #Refresh Platform Tree
        refresh_platform = QAction("Refresh &Platform Tree", self)
        refresh_platform.setShortcut('F2')
        refresh_platform.triggered.connect(self.actions.platform_tree_refresh)

        self.menu_actions.append(refresh_platform)

        #Setup Platform Tree
        self.platform_tree = PlatformTree(self, self.status, self.actions)
        self.platform_tree.setSizePolicy(QSizePolicy.Preferred,
                                    QSizePolicy.Preferred)

        #Add Nysa NysaBusView Tree View
        self.tab_view = QTabWidget()
        self.tab_view.setSizePolicy(QSizePolicy.Preferred,
                                    QSizePolicy.Preferred)
        self.fpga_image = NysaBusView(self.status, self.actions)
        self.fpga_image.setSizePolicy(QSizePolicy.MinimumExpanding,
                               QSizePolicy.Preferred)


        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.addWidget(self.platform_tree)
        self.main_splitter.addWidget(self.tab_view)

        self.main_splitter.setStretchFactor(1, 0)
        self.main_splitter.setSizePolicy(QSizePolicy.Preferred,
                                         QSizePolicy.MinimumExpanding)

        self.tm = TabManager(self.tab_view, self.status, self.actions)

        #Create the main window
        #Add Main Tabbed View
        layout.addWidget(self.main_splitter)
        self.add_tab(None, self.fpga_image, "Bus View", False)
        #Set the layout
        self.setLayout(layout)
        self.actions.platform_tree_changed_signal.connect(self.platform_tree_changed)

    def fit(self):
        self.fpga_image.scale_fit()

    def get_menu_actions(self):
        return self.menu_actions

    def platform_tree_changed(self, uid, nysa_type, nysa_dev):
        l = self.platform_tree.selectedIndexes()
        if len(l) == 0:
            return
        index = l[0]
        if index is None:
            return
        color = self.platform_tree.get_node_color(index)
        self.tm.set_tab_color(self.fpga_image, color)

    def get_nysa_bus_view(self):
        return self.fpga_image

    def add_tab(self, nysa_id, widget, name, removable = True):
        self.tm.add_tab(name, nysa_id, widget, False)

        if widget is not self.fpga_image:
            l = self.platform_tree.selectedIndexes()
            if len(l) == 0:
                return
            index = l[0]
            if index is None:
                return
            color = self.platform_tree.get_node_color(index)
            self.tm.set_tab_color(self.fpga_image, color)

    def remove_tab(self, index):
        self.tab_view.removeTab(index)


