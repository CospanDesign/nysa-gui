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

__author__ = 'email@example.com (name)'

import sys
import os

from PyQt4.QtGui import *
from PyQt4.QtCore import *


CHANNEL_NAME    =   0
READ_FULL       =   1
READ_EMPTY      =   2
READ_OVERFLOW   =   3
READ_ERROR      =   4
WRITE_EMPTY     =   5
WRITE_FULL      =   6
WRITE_UNDERFLOW =   7


class View(QWidget):

    def __init__(self, status = None, actions = None):
        super (View, self).__init__()
        self.status = status
        self.actions = actions


        self.setWindowTitle("Standalone View")
        layout = QVBoxLayout()
        control_layout = QFormLayout()

        channel_layout = QGridLayout()
        self.refresh_button = QPushButton("Refresh")

        layout.addWidget(self.refresh_button)
        layout.addLayout(control_layout)

        #Control Layout
        self.ddr3_reset_box = QCheckBox()
        self.ddr3_reset_box.setEnabled(False)
        self.calibration_done_box = QCheckBox()
        self.calibration_done_box.setEnabled(False)
        control_layout.addRow("DDR3 Reset", self.ddr3_reset_box)
        control_layout.addRow("Calibration Done", self.calibration_done_box)
        self.enable_boxes = []
        for i in range (0, 6):
            self.enable_boxes.append(QCheckBox())
            self.enable_boxes[i].setEnabled(False)

        for i in range (0, 6):
            control_layout.addRow("Channel: %d" % i, self.enable_boxes[i])

        layout.addLayout(channel_layout)
        channel_layout.addWidget(QLabel("Read Full"         ), 0, READ_FULL,       Qt.AlignCenter)
        channel_layout.addWidget(QLabel("Read Empty"        ), 0, READ_EMPTY,      Qt.AlignCenter)
        channel_layout.addWidget(QLabel("Read Overflow"     ), 0, READ_OVERFLOW,   Qt.AlignCenter)
        channel_layout.addWidget(QLabel("Read Error"        ), 0, READ_ERROR,      Qt.AlignCenter)
        channel_layout.addWidget(QLabel("Write Empty"       ), 0, WRITE_EMPTY,     Qt.AlignCenter)
        channel_layout.addWidget(QLabel("Write Full"        ), 0, WRITE_FULL,      Qt.AlignCenter)
        channel_layout.addWidget(QLabel("Write Underflow"   ), 0, WRITE_UNDERFLOW, Qt.AlignCenter)

        self.read_full_boxes = []
        self.read_empty_boxes = []
        self.read_overflow_boxes = []
        self.read_error_boxes = []
        self.write_empty_boxes = []
        self.write_full_boxes = []
        self.write_underflow_boxes = []

        for i in range (0, 6):
            self.read_full_boxes.append(QCheckBox())
            self.read_full_boxes[i].setEnabled(False)
            self.read_empty_boxes.append(QCheckBox())
            self.read_empty_boxes[i].setEnabled(False)
            self.read_overflow_boxes.append(QCheckBox())
            self.read_overflow_boxes[i].setEnabled(False)
            self.read_error_boxes.append(QCheckBox())
            self.read_error_boxes[i].setEnabled(False)
            self.write_empty_boxes.append(QCheckBox())
            self.write_empty_boxes[i].setEnabled(False)
            self.write_full_boxes.append(QCheckBox())
            self.write_full_boxes[i].setEnabled(False)
            self.write_underflow_boxes.append(QCheckBox())
            self.write_underflow_boxes[i].setEnabled(False)


        for i in range (0, 6):
            channel_layout.addWidget(QLabel("Channel: %d" % i)    , i + 1, CHANNEL_NAME,    Qt.AlignCenter)
            channel_layout.addWidget(self.read_full_boxes[i]      , i + 1, READ_FULL,       Qt.AlignCenter)
            channel_layout.addWidget(self.read_empty_boxes[i]     , i + 1, READ_EMPTY,      Qt.AlignCenter)
            channel_layout.addWidget(self.read_overflow_boxes[i]  , i + 1, READ_OVERFLOW,   Qt.AlignCenter)
            channel_layout.addWidget(self.read_error_boxes[i]     , i + 1, READ_ERROR,      Qt.AlignCenter)
            channel_layout.addWidget(self.write_empty_boxes[i]    , i + 1, WRITE_EMPTY,     Qt.AlignCenter)
            channel_layout.addWidget(self.write_full_boxes[i]     , i + 1, WRITE_FULL,      Qt.AlignCenter)
            channel_layout.addWidget(self.write_underflow_boxes[i], i + 1, WRITE_UNDERFLOW, Qt.AlignCenter)
            channel_layout.setRowStretch(i + 1, WRITE_UNDERFLOW)

        self.refresh_button.clicked.connect(self.refresh)


        self.setLayout(layout)

    def set_ddr3_reset(self, enable):
        self.ddr3_reset_box.setChecked(enable)

    def set_ddr3_calibration_done(self, enable):
        self.calibration_done_box.setChecked(enable)

    def set_channel_enable(self, channel, enable):
        self.enable_boxes[channel].setChecked(enable)

    def set_channel_status(self, channel, read_full, read_empty, read_overflow, read_error, write_empty, write_full, write_underflow):
        self.read_full_boxes[channel].setChecked(read_full)
        self.read_empty_boxes[channel].setChecked(read_empty)
        self.read_overflow_boxes[channel].setChecked(read_overflow)
        self.read_error_boxes[channel].setChecked(read_error)
        self.write_empty_boxes[channel].setChecked(write_empty)
        self.write_full_boxes[channel].setChecked(write_full)
        self.write_underflow_boxes[channel].setChecked(write_underflow)

    def refresh(self):
        self.status.Debug("Refresh")
        self.actions.artemis_refresh.emit()
        

        
