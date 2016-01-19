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


""" LAX Configuration Widget
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os
from functools import partial

from PyQt4.QtGui import QLabel
from PyQt4.QtCore import QSize
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QVBoxLayout

from PyQt4 import QtCore

#path = os.path.join(os.path.dirname(__file__),
#                             os.pardir,
#                             os.pardir,
#                             "common")
#path = os.path.abspath(path)
#sys.path.insert(0, path)

from register_view import RegisterView

direction_ss = os.path.join(os.path.dirname(__file__), "stylesheet.css")


TRIGGER_OFFSET     = 0
TRIGGER_REPEAT     = 1

class LaxTriggerWidget(QWidget):

    def __init__(self, actions = None):
        super (LaxTriggerWidget, self).__init__()
        self.actions = actions

        self.enable_button = QPushButton("Not Running (Press to Start)")
        self.enable_button.setCheckable(True)
        self.enable_button.clicked.connect(self.enable_clicked)

        self.reset_lax = QPushButton("Reset")
        self.reset_lax.clicked.connect(self.reset_logic_analyzer_clicked)

        self.restart_lax = QPushButton("Restart")
        self.restart_lax.clicked.connect(self.restart_logic_analyzer_clicked)

        self.register_view = RegisterView() 
        self.register_view.add_register(TRIGGER_OFFSET, "Trigger Offset", 0x00)
        self.register_view.add_register(TRIGGER_REPEAT, "Trigger Repeat", 0x00)
        self.register_view.get_pressed_signal.connect(self.register_view_get)
        self.register_view.set_pressed_signal.connect(self.register_view_set)

        layout = QVBoxLayout()
        layout.addWidget(self.enable_button)
        layout.addWidget(self.reset_lax)
        layout.addWidget(self.restart_lax)
        layout.addWidget(self.register_view)
        self.setLayout(layout)

    def sizeHint(self):
        size = QSize()
        size.setHeight(200)
        return size

    def restart_logic_analyzer_clicked(self):
        self.actions.restart_logic_analyzer.emit()

    def enable_clicked(self):
        self.enable_changed()
        self.actions.enable_capture.emit(not self.enable_button.isChecked())

    def enable_changed(self):
        if self.enable_button.isChecked():
            self.enable_button.setText("Running (Press to Stop)")
        else:
            self.enable_button.setText("Not Running (Press to Start)")

    def reset_logic_analyzer_clicked(self):
        self.actions.reset_logic_analyzer.emit()

    def register_view_get(self, index):
        if index == TRIGGER_OFFSET:
            self.actions.trigger_offset_update.emit()
        elif index == TRIGGER_REPEAT:
            self.actions.repeat_count_update.emit()

    def register_view_set(self, index):
        if index == TRIGGER_OFFSET:
            self.actions.trigger_offset_changed.emit()
        elif index == TRIGGER_REPEAT:
            self.actions.repeat_count_changed.emit()

    def update_enable(self, enable):
        self.enable_button.setChecked(not enable)
        self.enable_changed()

    def update_trigger_offset(self, value):
        self.register_view.set_register(TRIGGER_OFFSET, value)

    def update_repeat_count(self, value):
        self.register_view.set_register(TRIGGER_REPEAT, value)

    def get_trigger_offset(self):
        return self.register_view.get_register(TRIGGER_OFFSET)

    def get_repeat_count(self):
        return self.register_view.get_register(TRIGGER_REPEAT)
