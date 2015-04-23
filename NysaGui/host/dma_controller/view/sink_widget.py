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

from DMA_DEFINES import *

class SinkWidget(QWidget):

    def __init__(self, index):
        super (SinkWidget, self).__init__()
        self.index = index
        layout = QVBoxLayout()
        self.label = QLabel("Sink %d" % index)
        layout.addWidget(self.label)
        form_layout = QFormLayout()

        self.increment_addr = QCheckBox()
        self.increment_addr.stateChanged.connect(self.increment_addr_changed)
        self.decrement_addr = QCheckBox()
        self.decrement_addr.stateChanged.connect(self.decrement_addr_changed)
        self.respect_data_quantum = QCheckBox()
        self.respect_data_quantum.stateChanged.connect(self.respect_data_quantum_changed)
        self.commit_button = QPushButton("Commit")
        self.commit_button.clicked.connect(self.commit)

        form_layout.addRow(QString("Increment Address"), self.increment_addr)
        form_layout.addRow(QString("Decrement Address"), self.decrement_addr)
        form_layout.addRow(QString("Respect Data Quantum"), self.respect_data_quantum)
        form_layout.addRow(self.commit_button)
        layout.addLayout(form_layout)
        self.setLayout(layout)

        self.label.setStyleSheet("background-color: %s" % DMA_GOOD)

    def increment_addr_changed(self):
        value = self.increment_addr.isChecked()
        self.label.setStyleSheet("background-color: %s" % DMA_WARNING)

    def decrement_addr_changed(self):
        value = self.decrement_addr.isChecked()
        self.label.setStyleSheet("background-color: %s" % DMA_WARNING)

    def respect_data_quantum_changed(self):
        value = self.respect_data_quantum.isChecked()
        self.label.setStyleSheet("background-color: %s" % DMA_WARNING)

    def commit(self):
        self.label.setStyleSheet("background-color: %s" % DMA_GOOD)
