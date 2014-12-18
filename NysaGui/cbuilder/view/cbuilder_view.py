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

from NysaGui.common.project_tree import ProjectTree
from NysaGui.common.project_tab_manager import ProjectTabManager

class CBuilderView(QWidget):

    def __init__(self, actions, status):
        super (CBuilderView, self).__init__()
        layout = QVBoxLayout()
        self.setObjectName("cbuilder")
        self.status = status
        self.actions = actions
        self.menu_actions = []
        #Menu Actions
        self.new_core_action = QAction("New Core Wizard", self)
        self.new_core_action.triggered.connect(self.actions.cbuilder_new_core)
        self.menu_actions.append(self.new_core_action)

        self.project_tree = ProjectTree(self.actions, self.status)
        self.tab_view = QTabWidget()
        self.tab_view.setSizePolicy(QSizePolicy.Preferred,
                                    QSizePolicy.Preferred)

        self.tm = ProjectTabManager(self.tab_view, self.actions, self.status)



        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.addWidget(self.project_tree)
        self.main_splitter.addWidget(self.tab_view)

        self.main_splitter.setStretchFactor(1, 0)
        self.main_splitter.setSizePolicy(QSizePolicy.Preferred,
                                         QSizePolicy.MinimumExpanding)

        layout.addWidget(self.main_splitter)
        self.setLayout(layout)

    def get_menu_actions(self):
        return self.menu_actions

    def add_project(self, project):
        self.project_tree.add_project(project)
