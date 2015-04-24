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

class SourceWidget(QWidget):

    def __init__(self, status, actions, index, sink_count):
        super (SourceWidget, self).__init__()
        self.status = status
        self.actions = actions
        self.index = index
        layout = QVBoxLayout()
        self.label = QLabel("Source %d" % index)
        layout.addWidget(self.label)
        form_layout = QFormLayout()

        self.sink_addr_select = QComboBox()
        for i in range(sink_count):
            self.sink_addr_select.addItem(str(i))
        self.sink_addr_select.currentIndexChanged.connect(self.sink_addr_changed)
        self.increment_addr = QCheckBox()
        self.increment_addr.stateChanged.connect(self.increment_addr_changed)
        self.decrement_addr = QCheckBox()
        self.decrement_addr.stateChanged.connect(self.decrement_addr_changed)
        self.commit_button = QPushButton("Commit")
        self.commit_button.clicked.connect(self.commit)
        self.enable_button = QPushButton("Enable")
        self.enable_button.setCheckable(True)
        self.enable_button.clicked.connect(self.enable_clicked)

        form_layout.addRow(QString("Bind to Sink"), self.sink_addr_select)
        form_layout.addRow(QString("Increment Address"), self.increment_addr)
        form_layout.addRow(QString("Decrement Address"), self.decrement_addr)
        form_layout.addRow(self.commit_button)
        form_layout.addRow(self.enable_button)
        layout.addLayout(form_layout)
        self.setLayout(layout)
        self.label.setStyleSheet("background-color: %s" % DMA_GOOD)

    def increment_addr_changed(self):
        self.label.setStyleSheet("background-color: %s" % DMA_WARNING)

    def decrement_addr_changed(self):
        self.label.setStyleSheet("background-color: %s" % DMA_WARNING)

    def sink_addr_changed(self, index):
        self.label.setStyleSheet("background-color: %s" % DMA_WARNING)

    def update_settings(self, source_dict):
        self.sink_addr_select.setCurrentIndex(source_dict["SINK_ADDR"])
        self.increment_addr.setChecked(source_dict["INC_ADDR"])
        self.decrement_addr.setChecked(source_dict["DEC_ADDR"])
        self.label.setStyleSheet("background-color: %s" % DMA_GOOD)

    def commit(self):
        self.label.setStyleSheet("background-color: %s" % DMA_GOOD)
        #Get information from
        source_dict = {}
        source_dict["SINK_ADDR"] = self.sink_addr_select.currentIndex()
        source_dict["INC_ADDR"] = self.increment_addr.isChecked()
        source_dict["DEC_ADDR"] = self.decrement_addr.isChecked()
        self.actions.source_commit.emit(self.index, source_dict)

    def enable_clicked(self):
        value = self.enable_button.isDown()
        self.actions.enable_channel.emit(self.index, value)
