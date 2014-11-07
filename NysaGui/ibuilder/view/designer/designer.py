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

#from visual_graph.box import Box
#from box_list import BoxList


class Designer(QWidget):
    def __init__(self, actions, status, project):
        super (Designer, self).__init__()
        self.status = status
        self.actions = actions
        self.project = project
        layout = QVBoxLayout()
        self.setLayout(layout)

