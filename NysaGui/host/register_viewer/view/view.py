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
from PyQt4.QtGui import QVBoxLayout
sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir))


from NysaGui.host.common.register_view import RegisterView

class View(QWidget):

    def __init__(self, status = None, Actions = None):
        super (View, self).__init__()
        self.actions = Actions
        self.name = QLabel("Experimental")
        self.rv = RegisterView()
        self.rv.set_pressed_signal.connect(self.register_set_pressed)
        self.rv.get_pressed_signal.connect(self.register_get_pressed)
        layout = QVBoxLayout()
        layout.addWidget(self.name)
        layout.addWidget(self.rv)
        self.setLayout(layout)

    def set_name(self, name):
        self.name.setText(name)

    def add_register(self, index, name, initial_value = 0):
        self.rv.add_register(index, name, initial_value)

    def set_register(self, index, value):
        self.rv.set_register(index, value)

    def register_set_pressed(self, index, value):
        self.actions.set_pressed.emit(index, value)

    def register_get_pressed(self, index):
        self.actions.get_pressed.emit(index)


