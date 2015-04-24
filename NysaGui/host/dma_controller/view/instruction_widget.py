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


import sys
import os

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from DMA_DEFINES import *

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir))

from NysaGui.common.hex_validator import HexValidator

class InstructionWidget(QWidget):

    def __init__(self, status, actions, index, instruction_count):
        super (InstructionWidget, self).__init__()
        self.status = status
        self.actions = actions
        self.instruction_count = instruction_count
        self.index = index
        self.label = QLabel("Instruction %d" % index)
        form_layout = QFormLayout()

        self.source_address = QLineEdit("0x00000000")
        hv = HexValidator()
        hv.setRange(0, 0xFFFFFFFFFFFFFFFF)
        self.source_address.setValidator(hv)
        self.source_address.textChanged.connect(self.source_addr_changed)
        self.sink_address = QLineEdit("0x00000000")
        hv = HexValidator()
        hv.setRange(0, 0xFFFFFFFFFFFFFFFF)
        self.sink_address.setValidator(hv)
        self.sink_address.textChanged.connect(self.sink_addr_changed)
        v = QDoubleValidator()
        v.setRange(0, 0xFFFFFFFF)
        self.data_count = QLineEdit()
        self.data_count.setValidator(v)
        self.data_count.textChanged.connect(self.data_count_changed)
        self.data_count_changed(self.data_count.text())

        #Populate with all the instruction indexes
        self.next_instruction = QComboBox()
        self.next_instruction.currentIndexChanged.connect(self.next_inst_changed)
        self.bond_ingress_addr = QComboBox()
        self.bond_ingress_addr.currentIndexChanged.connect(self.ingress_addr_changed)
        self.bond_egress_addr = QComboBox()
        self.bond_egress_addr.currentIndexChanged.connect(self.egress_addr_changed)
        for i in range (self.instruction_count):
            self.next_instruction.addItem(str(i))
            self.bond_ingress_addr.addItem(str(i))
            self.bond_egress_addr.addItem(str(i))

        self.next_instruction.setCurrentIndex(0)
        self.bond_ingress_addr.setCurrentIndex(0)
        self.bond_egress_addr.setCurrentIndex(0)

        self.reset_src_addr_on_command = QCheckBox()
        self.reset_dest_addr_on_command = QCheckBox()
        self.enable_bond_ingress = QCheckBox()
        self.enable_bond_egress = QCheckBox()
        self.cmd_continue = QCheckBox()
        self.commit_button = QPushButton("Commit")

        self.reset_src_addr_on_command.stateChanged.connect(self.reset_src_addr_on_command_changed)
        self.reset_dest_addr_on_command.stateChanged.connect(self.reset_dest_addr_on_command_changed)
        self.enable_bond_ingress.stateChanged.connect(self.enable_ingress_changed)
        self.enable_bond_egress.stateChanged.connect(self.enable_egress_changed)
        self.cmd_continue.stateChanged.connect(self.cmd_continue_changed)
        self.commit_button.clicked.connect(self.commit)

        form_layout.addRow(self.label)
        form_layout.addRow(QString("Reset Source Address on New Instruction"), self.reset_src_addr_on_command)
        form_layout.addRow(QString("Reset Dest Address on New Instruction"), self.reset_dest_addr_on_command)
        form_layout.addRow(QString("Source Address"), self.source_address)
        form_layout.addRow(QString("Sink Address"), self.sink_address)
        form_layout.addRow(QString("Continue Command"), self.cmd_continue)
        form_layout.addRow(QString("Data Count"), self.data_count)
        form_layout.addRow(QString("Next Instruction"), self.next_instruction)
        form_layout.addRow(QString("Enable Bond Ingress"), self.enable_bond_ingress)
        form_layout.addRow(QString("Bond Ingress Instruction addr"), self.bond_ingress_addr)
        form_layout.addRow(QString("Enable Bond Egress"), self.enable_bond_egress)
        form_layout.addRow(QString("Bond Egress Instruction addr"), self.bond_egress_addr)
        form_layout.addRow(self.commit_button)

        self.setLayout(form_layout)
        self.label.setStyleSheet("background-color: %s" % DMA_GOOD)

    def next_inst_changed(self, index):
        self.label.setStyleSheet("background-color: %s" % DMA_WARNING)

    def egress_addr_changed(self, index):
        self.label.setStyleSheet("background-color: %s" % DMA_WARNING)

    def ingress_addr_changed(self, index):
        self.label.setStyleSheet("background-color: %s" % DMA_WARNING)

    def reset_src_addr_on_command_changed(self):
        value = self.reset_src_addr_on_command.isChecked()
        self.label.setStyleSheet("background-color: %s" % DMA_WARNING)

    def reset_dest_addr_on_command_changed(self):
        value = self.reset_dest_addr_on_command.isChecked()
        self.label.setStyleSheet("background-color: %s" % DMA_WARNING)

    def enable_ingress_changed(self):
        self.label.setStyleSheet("background-color: %s" % DMA_WARNING)

    def enable_egress_changed(self):
        self.label.setStyleSheet("background-color: %s" % DMA_WARNING)

    def cmd_continue_changed(self):
        self.label.setStyleSheet("background-color: %s" % DMA_WARNING)
        
    def source_addr_changed(self, data):
        self.label.setStyleSheet("background-color: %s" % DMA_WARNING)
        
    def sink_addr_changed(self, data):
        self.label.setStyleSheet("background-color: %s" % DMA_WARNING)

    def data_count_changed(self, data):
        self.label.setStyleSheet("background-color: %s" % DMA_WARNING)
        v = self.data_count.validator()
        state = v.validate(data, 0)[0]
        color = DMA_ERROR
        if state == QValidator.Acceptable:
            color = DMA_GOOD
        elif state == QValidator.Intermediate:
            color = DMA_WARNING
        else:
            color = DMA_ERROR
        self.data_count.setStyleSheet('QLineEdit { background-color: %s }' % color)

    def commit(self):
        self.label.setStyleSheet("background-color: %s" % DMA_GOOD)

