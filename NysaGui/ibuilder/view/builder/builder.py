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

from info_view import InfoView
from tool_properties_view import ToolPropertiesView
from build_flow_view import BuildFlowView

class Builder(QWidget):

    def __init__(self, actions, status):
        super (Builder, self).__init__()
        self.status = status
        self.actions = actions
        self.config = {}

        layout = QVBoxLayout()

        self.info = InfoView(actions, status)
        self.bfv = BuildFlowView(actions, status)
        self.tpv = ToolPropertiesView(actions, status)
        layout.addWidget(self.info)
        layout.addWidget(self.bfv)
        layout.addWidget(self.tpv)
        self.setLayout(layout)

    def set_project_name(self, name):
        self.info.set_project_name(None, name)

    def set_project_directory(self, path):
        self.info.set_project_directory(path)

    def set_board_dict(self, board_dict):
        self.info.set_board_dict(board_dict)

    def set_project_status(self, status):
        self.info.set_status(status)
