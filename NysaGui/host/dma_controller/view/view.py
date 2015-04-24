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

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import Qt

from source_widget import SourceWidget
from sink_widget import SinkWidget
from instruction_widget import InstructionWidget

class View(QWidget):

    def __init__(self, status = None, actions = None):
        super (View, self).__init__()
        self.actions = actions
        self.status = status

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
        self.sources = []
        self.sinks = []
        self.instructions = []

    def setup(self, source_count, instruction_count, sink_count):
        self.source_count = source_count
        self.instruction_count = instruction_count
        self.sink_count = sink_count
        self.status.Verbose("Source count: %d" % self.source_count)
        self.status.Verbose("Instruction count: %d" % self.instruction_count)
        self.status.Verbose("Sink count: %d" % self.sink_count)

        for i in reversed(range(self.columns_layout.count())):
            item = self.columns_layout.itemAt(i)
            self.columns_layout.removeItem(item)

        self.source_layout = QScrollArea()
        self.instruction_layout = QScrollArea()
        self.sink_layout = QScrollArea()

        #Source Boxes
        self.sourcs = []
        self.sinks = []
        self.instructions = []

        sa = QGroupBox()
        fl = QVBoxLayout()
        for s in range(self.source_count):
            sw = SourceWidget(self.status, self.actions, s, self.instruction_count, self.sink_count)
            self.sources.append(sw)
            fl.addWidget(sw)
        #sa.setLayout(fl)
        #self.source_layout.setWidget(sa)
        self.source_layout = fl

        #Instruction Boxes
        sa = QGroupBox()
        fl = QVBoxLayout()
        for s in range(self.instruction_count):
            sw = InstructionWidget(self.status, self.actions, s, self.instruction_count)
            self.instructions.append(sw)
            fl.addWidget(sw)
        sa.setLayout(fl)
        self.instruction_layout.setWidget(sa)

        #Sink Boxes
        sa = QGroupBox()
        fl = QVBoxLayout()
        for s in range(self.sink_count):
            sw = SinkWidget(self.status, self.actions, s)
            self.sinks.append(sw)
            fl.addWidget(sw)
        #sa.setLayout(fl)
        #self.sink_layout.setWidget(sa)
        self.sink_layout = fl

        #self.columns_layout.addWidget(self.source_layout)
        self.columns_layout.addLayout(self.source_layout)
        self.columns_layout.addWidget(self.instruction_layout)
        #self.columns_layout.addWidget(self.sink_layout)
        self.columns_layout.addLayout(self.sink_layout)

        self.update()

    def update_source_settings(self, index, source_dict):
        self.sources[index].update_settings(source_dict)

    def update_instruction_settings(self, index, instruction_dict):
        self.instructions[index].update_settings(instruction_dict)

    def update_sink_settings(self, index, sink_dict):
        self.sinks[index].update_settings(sink_dict)

