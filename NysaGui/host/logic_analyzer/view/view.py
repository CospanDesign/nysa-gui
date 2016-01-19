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

from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QTextEdit

from lax_config_view import LaxConfigWidget
from lax_trigger_view import LaxTriggerWidget

from save_loader import SaveLoader

DEFAULT_FILE_PATH = os.path.join(os.path.expanduser("~"), "capture.vcd")


class View(QWidget):

    def __init__(self, status = None, Actions = None):
        super (View, self).__init__()
        self.actions = Actions

    def setup_view(self):
        self.setWindowTitle("Standalone View")
        self.file_controller = SaveLoader(extensions = ["vcd"], initial_file = DEFAULT_FILE_PATH, save_only = True)
        layout = QHBoxLayout()
        tlayout = QVBoxLayout()
        tlayout.addWidget(QLabel("Logic Analyzer Configuration"))
        tlayout.addWidget(self.file_controller)

        self.config_view = LaxConfigWidget(count = 32, actions = self.actions)
        self.trigger_view = LaxTriggerWidget(self.actions)
        layout.addWidget(self.config_view)
        tlayout.addWidget(self.trigger_view)
        layout.addLayout(tlayout)

        self.setLayout(layout)

    def get_save_filepath(self):
        return self.file_controller.get_filename()
        
    def get_trigger_enable(self):
        return self.config_view.get_trigger_enable()

    def get_trigger_polarity(self):
        return self.config_view.get_trigger_polarity()

    def get_trigger_offset(self):
        return self.trigger_view.get_trigger_offset()

    def get_repeat_count(self):
        return self.trigger_view.get_repeat_count()

    def update_trigger_enable(self, value):
        self.config_view.update_all_enable(value)

    def update_trigger_polarity(self, value):
        self.config_view.update_trigger_polarity(value)

    def update_enable(self, enable):
        self.trigger_view.update_enable(True)

    def update_trigger_offset(self, offset):
        self.trigger_view.update_trigger_offset(offset)

    def update_repeat_count(self, count):
        self.trigger_view.update_repeat_count(count)
