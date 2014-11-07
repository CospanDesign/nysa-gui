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

from platform_tree.platform_tree import PlatformTree
p = os.path.join(os.path.dirname(__file__), 
                 os.pardir)
p = os.path.abspath(p)
sys.path.append(p)

from visualizer.visualizer_widget import VisualizerWidget

class MainPanel(QWidget):
    def __init__(self, actions):
        super(MainPanel, self).__init__()
        self.actions = actions

        self.platform_tree = PlatformTree(self.actions, self)
        self.add_core_button = QPushButton("Add Verilog Core")
        self.add_image_button = QPushButton("Add Image")

        self.image_view = VisualizerWidget(self.actions)

        layout = QVBoxLayout()
        view_layout = QHBoxLayout()

        view_layout.addWidget(self.platform_tree)
        view_layout.addWidget(self.image_view)

        layout.addLayout(view_layout)
        layout.addWidget(self.add_core_button)
        layout.addWidget(self.add_image_button)

        self.setLayout(layout)
        self.show()
        self.add_core_button.clicked.connect(self.add_core_clicked)
        self.add_image_button.clicked.connect(self.add_image_clicked)

    def add_core_clicked(self):
        self.actions.add_verilog_core.emit("test", {})

    def add_image_clicked(self):
        self.actions.add_image_config.emit({})

class MainForm(QMainWindow):
    def __init__(self, actions):
        super (MainForm, self).__init__()
        self.actions = actions
        self.setWindowTitle("Nysa Host")
        self.setCentralWidget(MainPanel(self.actions))
        self.show()


