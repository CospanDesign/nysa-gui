# Copyright (c) 2015 Dave McCoy (dave.mccoy@cospandesign.com)

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

__author__ = 'dave.mccoy@cospandesign.com (name)'

import sys
import os

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QTextEdit
from PyQt4.QtGui import QLabel
from PyQt4 import Qt

from source_widget import SourceWidget

class View(QWidget):

    def __init__(self, status = None, Actions = None):
        super (View, self).__init__()

        self.setWindowTitle("Standalone View")
        layout = QVBoxLayout()
        dma_label = QLabel("DMA Controller")
        dma_label.setSizePolicy(Qt.QSizePolicy.Minimum, Qt.QSizePolicy.Maximum)

        layout.addWidget(dma_label)
        self.source_layout = QVBoxLayout()
        self.instruction_layout = QVBoxLayout()
        self.sink_layout = QVBoxLayout()

        self.columns_layout = QHBoxLayout()
        self.columns_layout.addLayout(self.source_layout)
        self.columns_layout.addLayout(self.instruction_layout)
        self.columns_layout.addLayout(self.sink_layout)

        layout.addLayout(self.columns_layout)
        self.setLayout(layout)

    def setup(self, source_count, instruction_count, sink_count):
        self.source_count = source_count
        self.instruction_count = instruction_count
        self.sink_count = sink_count
        #self.columns_layout.removeItem(self.source_layout)
        #self.columns_layout.removeItem(self.instruction_layout)
        #self.columns_layout.removeItem(self.sink_layout)

        for i in reversed(range(self.columns_layout.count())): 
            item = self.columns_layout.itemAt(i)
            self.columns_layout.removeItem(item)

        self.source_layout = QVBoxLayout()
        self.instruction_layout = QVBoxLayout()
        self.sink_layout = QVBoxLayout()
        for s in range(self.source_count):
            print "Source: %d" % s
            sw = SourceWidget(s)
            self.source_layout.addWidget(sw)

        self.columns_layout.addLayout(self.source_layout)
        self.columns_layout.addLayout(self.instruction_layout)
        self.columns_layout.addLayout(self.sink_layout)
        self.update()



       
