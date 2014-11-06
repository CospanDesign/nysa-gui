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

from configuration.configuration import Configuration
from constraints.constraints import Constraints
from designer.designer import Designer
from builder.builder import Builder

class ProjectView(QWidget):

    def __init__(self,
                 actions,
                 status,
                 project_node):
        super (ProjectView, self).__init__()
        self.actions = actions
        self.status = status
        self.tab_view = QTabWidget()
        self.tab_view.setTabPosition(QTabWidget.South)
        self.tab_view.setTabShape(QTabWidget.Triangular)
        self.tab_view.setTabsClosable(False)
        layout = QVBoxLayout()
        layout.addWidget(self.tab_view)
        self.setLayout(layout)

        self.designer = Designer(actions, status, project_node.get_project())
        self.builder = Builder(actions, status, project_node.get_project())
        self.constraints = Constraints(actions, status, project_node.get_project())
        self.configuration = Configuration(actions, status, project_node.get_project())

        self.setup_tabs(project_node)

    def setup_tabs(self, project_node):
        
        designer_node = project_node.childWithKey("designer")
        builder_node = project_node.childWithKey("builder")
        constraint_node = project_node.childWithKey("constraints")
        configuration_node = project_node.childWithKey("configuration")

        color = designer_node.get_color(1)
        pm = QPixmap(QSize(16, 16))
        pm.fill(color)
        icon = QIcon(pm)
        self.tab_view.addTab(self.designer, icon, "designer")

        color = builder_node.get_color(1)
        pm = QPixmap(QSize(16, 16))
        pm.fill(color)
        icon = QIcon(pm)
        self.tab_view.addTab(self.builder, icon, "builder")

        color = constraint_node.get_color(1)
        pm = QPixmap(QSize(16, 16))
        pm.fill(color)
        icon = QIcon(pm)
        self.tab_view.addTab(self.constraints, icon, "constraints")

        color = configuration_node.get_color(1)
        pm = QPixmap(QSize(16, 16))
        pm.fill(color)
        icon = QIcon(pm)
        self.tab_view.addTab(self.configuration, icon, "configuration")

