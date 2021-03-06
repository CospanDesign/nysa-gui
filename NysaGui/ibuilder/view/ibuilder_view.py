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

from NysaGui.common.project_tree import ProjectTree
from NysaGui.common.project_tab_manager import ProjectTabManager

class IBuilderView(QWidget):
    def __init__(self, gui_actions, actions, status):
        super (IBuilderView, self).__init__()
        self.setObjectName("ibuilder")
        layout = QVBoxLayout()
        self.gui_actions = gui_actions
        self.status = status
        self.actions = actions
        self.menu_actions = []

        #Setup Project Side View
        self.project_tree = ProjectTree(self.actions, self.status)
        #Setup Module Side Pane
        #Create the main view
        self.tab_view = QTabWidget()
        self.tab_view.setSizePolicy(QSizePolicy.Preferred,
                                    QSizePolicy.Preferred)

        self.tm = ProjectTabManager(self.tab_view, self.actions, self.status)

        #self.main_view = IBuilderMainView(actions, status)
        #self.main_view.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)

        #Menu Actions
        self.new_project_action = QAction("New Project", self)
        self.new_project_action.triggered.connect(self.actions.ibuilder_new_project)
        self.menu_actions.append(self.new_project_action)

        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.addWidget(self.project_tree)
        self.main_splitter.addWidget(self.tab_view)

        self.main_splitter.setStretchFactor(1, 0)
        self.main_splitter.setSizePolicy(QSizePolicy.Preferred,
                                         QSizePolicy.MinimumExpanding)

        layout.addWidget(self.main_splitter)
        self.setLayout(layout)
        #self.setFocusPolicy(Qt.WheelFocus)
        #self.show()

    def get_menu_actions(self):
        return self.menu_actions

    def add_project(self, project):
        project_node = self.project_tree.add_project(project)
        self.tm.add_tab(project_node.get_name(), project.get_view())
        self.project_tree.reset()

    def remove_project(self, name, path = None):
        p = self.project_tree.remove_project(name, path)
        self.tm.remove_tab(name)
        return p

    def get_project_tree(self):
        return self.project_tree

    def get_current_project_name(self):
        tw = self.tab_view.currentWidget()
        return tw.get_controller().get_project_name()

    def clear_projects(self):
        self.tm.clear()
        self.project_tree.clear()


