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


from PyQt4.QtGui import *
from PyQt4.QtCore import *

class SourceWidget(QWidget):

    def __init__(self, index):
        super (SourceWidget, self).__init__()
        self.index = index
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Source %d" % index))
        form_layout = QFormLayout()

        self.increment_addr = QCheckBox()
        self.increment_addr.stateChanged.connect(self.increment_addr_changed)
        self.decrement_addr = QCheckBox()
        self.decrement_addr.stateChanged.connect(self.decrement_addr_changed)
        self.reset_addr_on_command = QCheckBox()
        self.reset_addr_on_command.stateChanged.connect(self.reset_addr_on_command_changed)

        form_layout.addRow(QString("Increment Address"), self.increment_addr)
        form_layout.addRow(QString("Decrement Address"), self.decrement_addr)
        form_layout.addRow(QString("Reset Address on New Instruction"), self.reset_addr_on_command)
        layout.addLayout(form_layout)
        self.setLayout(layout)

    def increment_addr_changed(self):
        value = self.increment_addr.isChecked()

    def decrement_addr_changed(self):
        value = self.decrement_addr.isChecked()

    def reset_addr_on_command_changed(self):
        value = self.reset_addr_on_command.isChecked()
        
