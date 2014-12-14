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

        #Place Holder
        l = QLabel("CBuilder")
        l.setObjectName("cbuilder")
        layout.addWidget(l)
        #Set the layout of the widget
        self.setLayout(layout)

    def get_menu_actions(self):
        return self.menu_actions


