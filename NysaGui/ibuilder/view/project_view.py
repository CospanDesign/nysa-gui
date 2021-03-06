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

from designer.designer import Designer
from configuration.configuration import Configuration
from constraints.constraints import Constraints
from builder.builder import Builder

CONFIG_DICT = {
    "designer":QColor(0xD7, 0xFF, 0xD7),
    "configuration":QColor(0xFF, 0xFF, 0xD7),
    "constraints":QColor(0xD7, 0xFF, 0xFF),
    "builder":QColor(0xFF, 0xD7, 0xFF),
}


VIEWS = ("designer", "constraints", "configuration", "builder")

class ProjectView(QWidget):

    def __init__(self, actions, status, xmsgs):
        super (ProjectView, self).__init__()
        self.actions = actions
        self.status = status
        self.xmsgs = xmsgs
        self.tab_view = QTabWidget()
        self.tab_view.setTabPosition(QTabWidget.South)
        self.tab_view.setTabShape(QTabWidget.Triangular)
        self.tab_view.setTabsClosable(False)
        layout = QVBoxLayout()
        layout.addWidget(self.tab_view)
        self.setLayout(layout)

        self.designer = Designer(actions, status)
        self.builder = Builder(actions, status, xmsgs)
        self.configuration = Configuration(actions, status)
        self.constraints = Constraints(actions, status)

        self.add_tab("designer", self.designer)
        self.add_tab("configuration", self.configuration)
        self.add_tab("constraints", self.constraints)
        self.add_tab("builder", self.builder)
        self.controller = None
        self.builder.set_project_status("Loaded default project")

    def set_controller(self, controller):
        self.designer.set_controller(controller)
        self.constraints.set_controller(controller)
        self.builder.set_controller(controller)
        self.controller = controller
        self.actions.update_view.emit()
        #controller.initialize_constraint_editor(self.constraints)

    def get_controller(self):
        return self.controller

    def update_view(self):
        self.actions.update_view.emit()

    def get_desigenr_scene(self):
        return self.designer.get_scene()

    def get_constraint_editor(self):
        return self.constraints

    def get_view_names(self):
        return VIEWS

    def add_tab(self, name, view):
        color = CONFIG_DICT[str(name)]
        pm = QPixmap(QSize(16, 16))
        pm.fill(color)
        icon = QIcon(pm)
        self.tab_view.addTab(view, icon, name)

    def get_designer_scene(self):
        return self.designer.get_scene()

    def get_color(self, name):
        return CONFIG_DICT[str(name)]

    def get_configuration_editor(self):
        return self.configuration

