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


class View(QWidget):

    def __init__(self, status = None, actions = None):
        super (View, self).__init__()
        self.status = status
        self.actions = actions

        self.setWindowTitle("Artemis USB2 Platform")
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh)

        #Controller
        self.sata_reset_checkbox = QCheckBox()
        self.command_layer_reset_checkbox = QCheckBox()
        self.en_hd_int = QCheckBox()
        self.en_dma_activate_int = QCheckBox()
        self.en_d2h_reg_int = QCheckBox()
        self.en_pio_setup_int = QCheckBox()
        self.en_d2h_data_int = QCheckBox()
        self.en_dma_setup_int = QCheckBox()
        self.en_set_device_bits_int = QCheckBox()

        self.sata_reset_checkbox.clicked.connect(self.sata_reset_checkbox_changed)
        self.command_layer_reset_checkbox.clicked.connect(self.command_layer_reset_changed)
        self.en_hd_int.clicked.connect(self.en_hd_int_changed)
        self.en_dma_activate_int.clicked.connect(self.en_dma_activate_int_changed)
        self.en_d2h_reg_int.clicked.connect(self.en_d2h_reg_int_changed)
        self.en_pio_setup_int.clicked.connect(self.en_pio_setup_int_changed)
        self.en_d2h_data_int.clicked.connect(self.en_d2h_data_int_changed)
        self.en_dma_setup_int.clicked.connect(self.en_dma_setup_int_changed)
        self.en_set_device_bits_int.clicked.connect(self.en_set_device_bits_int_changed)

        #Status
        self.reset_active_checkbox = QCheckBox()
        self.reset_active_checkbox.setEnabled(False)
        self.platform_ready = QCheckBox()
        self.platform_ready.setEnabled(False)
        self.platform_error = QCheckBox()
        self.platform_error.setEnabled(False)
        self.linkup = QCheckBox()
        self.linkup.setEnabled(False)
        self.rx_comm_init_detect = QCheckBox()
        self.rx_comm_init_detect.setEnabled(False)
        self.rx_comm_wake_detect = QCheckBox()
        self.rx_comm_wake_detect.setEnabled(False)
        self.tx_comm_reset = QCheckBox()
        self.tx_comm_reset.setEnabled(False)
        self.tx_comm_wake = QCheckBox()
        self.tx_comm_wake.setEnabled(False)
        self.tx_oob_complete = QCheckBox()
        self.tx_oob_complete.setEnabled(False)


        self.command_layer_ready = QCheckBox()
        self.command_layer_ready.setEnabled(False)
        self.transport_layer_ready = QCheckBox()
        self.transport_layer_ready.setEnabled(False)
        self.link_layer_ready = QCheckBox()
        self.link_layer_ready.setEnabled(False)
        self.phy_layer_ready = QCheckBox()
        self.phy_layer_ready.setEnabled(False)

        self.sata_busy = QCheckBox()
        self.sata_busy.setEnabled(False)
        self.hard_drive_error = QCheckBox()
        self.hard_drive_error.setEnabled(False)
        self.pio_data_ready = QCheckBox()
        self.pio_data_ready.setEnabled(False)

        #Hard Drive Status
        self.d2h_interrupt = QCheckBox()
        self.d2h_interrupt.setEnabled(False)
        self.d2h_notification = QCheckBox()
        self.d2h_notification.setEnabled(False)
        self.d2h_pmult = QLineEdit()
        self.d2h_pmult.setEnabled(False)
        self.d2h_status = QLineEdit()
        self.d2h_status.setEnabled(False)
        self.d2h_error = QLineEdit()
        self.d2h_error.setEnabled(False)
        self.oob_state = QLineEdit()
        self.oob_state.setEnabled(False)
        self.debug_linkup_data = QLineEdit()
        self.debug_linkup_data.setEnabled(False)

        self.d2h_lba = QLineEdit()
        self.d2h_lba.setEnabled(False)

        self.d2h_fis = QLineEdit()
        self.d2h_fis.setEnabled(False)

        d2h_status_layout = QHBoxLayout()
        self.d2h_status_bsy = QCheckBox("Busy")
        self.d2h_status_bsy.setEnabled(False)
        self.d2h_status_drdy = QCheckBox("Drive Ready")
        self.d2h_status_drdy.setEnabled(False)
        self.d2h_status_dwf = QCheckBox("Drive Write Fault")
        self.d2h_status_dwf.setEnabled(False)
        self.d2h_status_dsc = QCheckBox("Drive Seek Complete")
        self.d2h_status_dsc.setEnabled(False)
        self.d2h_status_drq = QCheckBox("Data Request Bit")
        self.d2h_status_drq.setEnabled(False)
        self.d2h_status_corr = QCheckBox("Corrected Data Error")
        self.d2h_status_corr.setEnabled(False)
        self.d2h_status_idx = QCheckBox("Index Bit")
        self.d2h_status_idx.setEnabled(False)
        self.d2h_status_err = QCheckBox("Error")
        self.d2h_status_err.setEnabled(False)

        d2h_status_layout.addWidget(self.d2h_status_bsy)
        d2h_status_layout.addWidget(self.d2h_status_drdy)
        d2h_status_layout.addWidget(self.d2h_status_dwf)
        d2h_status_layout.addWidget(self.d2h_status_dsc)
        d2h_status_layout.addWidget(self.d2h_status_drq)
        d2h_status_layout.addWidget(self.d2h_status_corr)
        d2h_status_layout.addWidget(self.d2h_status_idx)
        d2h_status_layout.addWidget(self.d2h_status_err)


        d2h_error_layout1 = QHBoxLayout()
        d2h_error_layout2 = QHBoxLayout()

        self.d2h_error_bbk = QCheckBox("Bad Block")
        self.d2h_error_bbk.setEnabled(False)
        
        self.d2h_error_unc = QCheckBox("Uncorrectable Data")
        self.d2h_error_unc.setEnabled(False)

        self.d2h_error_mc = QCheckBox("MC?")
        self.d2h_error_mc.setEnabled(False)

        self.d2h_error_idnf = QCheckBox("Sector Not Found")
        self.d2h_error_idnf.setEnabled(False)

        self.d2h_error_mcr = QCheckBox("MCR?")
        self.d2h_error_mcr.setEnabled(False)

        self.d2h_error_abrt = QCheckBox("Command Abort")
        self.d2h_error_abrt.setEnabled(False)

        self.d2h_error_tk0nf = QCheckBox("Track 0 Not Found")
        self.d2h_error_tk0nf.setEnabled(False)

        self.d2h_error_amnf = QCheckBox("Correct ID, Addr Not Found")
        self.d2h_error_amnf.setEnabled(False)

        d2h_error_layout1.addWidget(self.d2h_error_bbk)
        d2h_error_layout1.addWidget(self.d2h_error_unc)
        d2h_error_layout1.addWidget(self.d2h_error_mc)
        d2h_error_layout1.addWidget(self.d2h_error_idnf)

        d2h_error_layout2.addWidget(self.d2h_error_mcr)
        d2h_error_layout2.addWidget(self.d2h_error_abrt)
        d2h_error_layout2.addWidget(self.d2h_error_tk0nf)
        d2h_error_layout2.addWidget(self.d2h_error_amnf)


        hard_drive_command_layout = QHBoxLayout()
        self.command_combo = QComboBox()
        self.command_combo.addItems(["NOP", "Get Max Address Size", "Software Reset", "Idle"])
        self.command_combo.setCurrentIndex(1)
        self.command_go = QPushButton("Send Command")
        self.command_go.clicked.connect(self.send_command)
        hard_drive_command_layout.addWidget(self.command_combo)
        hard_drive_command_layout.addWidget(self.command_go)

        control_layout = QFormLayout()
        control_layout.addRow("SATA Control", QLabel("Control the Hard drive"))
        control_layout.addRow("Reset SATA Stack", self.sata_reset_checkbox)
        control_layout.addRow("SATA Command Layer Reset", self.command_layer_reset_checkbox)
        control_layout.addRow("Interrupt Registers", QLabel("Set or clear the following interrupt enable registers"))
        control_layout.addRow("Hard Drive Interrupt Enable", self.en_hd_int)
        control_layout.addRow("DMA Activate Interrupt Enable", self.en_dma_activate_int)
        control_layout.addRow("PIO Setup Interrupt Enalbe", self.en_pio_setup_int)
        control_layout.addRow("D2H Register Ready Interrupt Enable", self.en_d2h_reg_int)
        control_layout.addRow("D2H Data Ready Interrupt Enable", self.en_d2h_data_int)
        control_layout.addRow("DMA Setup Interrupt Enable", self.en_dma_setup_int)
        control_layout.addRow("Enable Set Device Bits Interrupt Enable", self.en_set_device_bits_int)

        control_layout.addRow("Status", QLabel("Display SATA stack status"))
        control_layout.addRow("Platform Ready", self.platform_ready)
        control_layout.addRow("Platform Error", self.platform_error)
        control_layout.addRow("Reset In Progress", self.reset_active_checkbox)
        control_layout.addRow("Hard Drive Linkup", self.linkup)
        control_layout.addRow("SATA Busy", self.sata_busy)
        control_layout.addRow("Hard Drive Error", self.hard_drive_error)
        control_layout.addRow("Peripheral I/O Data Ready", self.pio_data_ready)
        #control_layout.addRow("RX COMM INIT Detect", self.rx_comm_init_detect)
        #control_layout.addRow("RX COMM WAKE Detect", self.rx_comm_wake_detect)
        #control_layout.addRow("TX COMM RESET", self.tx_comm_reset)
        #control_layout.addRow("TX COMM WAKE", self.tx_comm_wake)
        #control_layout.addRow("TX OOB Complete", self.tx_oob_complete)
        control_layout.addRow("Hard Drive Command", hard_drive_command_layout)

        control_layout.addRow("SATA Stack Layer Ready", QLabel("Show SATA Layer is ready or not"))
        control_layout.addRow("Command Layer Ready", self.command_layer_ready)
        control_layout.addRow("Transport Layer Ready", self.transport_layer_ready)
        control_layout.addRow("Link Layer Ready", self.link_layer_ready)
        control_layout.addRow("Phy Layer Ready", self.phy_layer_ready)

        control_layout.addRow("SATA D2H Status", QLabel("D2H Status"))
        control_layout.addRow("D2H FIS", self.d2h_fis)
        control_layout.addRow("D2H Status", self.d2h_status)
        control_layout.addRow("D2H Status Bits", d2h_status_layout)
        control_layout.addRow("D2H Error", self.d2h_error)
        control_layout.addRow("D2H Error Bits 1", d2h_error_layout1)
        control_layout.addRow("D2H Error Bits 2", d2h_error_layout2)
        control_layout.addRow("Hard Drive LBA", self.d2h_lba)

        control_layout.addRow("SATA D2H Interrupt Status", QLabel("Interrupt Status"))
        control_layout.addRow("D2H Port Multiplier", self.d2h_pmult)
        control_layout.addRow("D2H Interrupt", self.d2h_interrupt)
        control_layout.addRow("D2H Notification", self.d2h_notification)

        #control_layout.addRow("Debug", QLabel("Debug Info"))
        #control_layout.addRow("OOB State", self.oob_state)
        #control_layout.addRow("Debug Linkup Data", self.debug_linkup_data)

        layout = QVBoxLayout()
        layout.addWidget(self.refresh_button)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        groupbox = QGroupBox("SATA")
        groupbox.setLayout(control_layout)
        scroll.setWidget(groupbox)

        layout.addWidget(scroll)

        self.setLayout(layout)

    def refresh(self):
        self.status.Debug("Refresh")
        self.actions.sata_refresh.emit()

    def command_layer_reset_changed(self, enable):
        self.actions.sata_command_layer_reset.emit(enable)

    def en_hd_int_changed(self, enable):
        self.actions.en_hd_int_changed.emit(enable)

    def en_dma_activate_int_changed(self, enable):
        self.actions.en_dma_activate_int_changed.emit(enable)

    def en_d2h_reg_int_changed(self, enable):
        self.actions.en_d2h_reg_int_changed.emit(enable)

    def en_pio_setup_int_changed(self, enable):
        self.actions.en_pio_setup_int_changed.emit(enable)

    def en_d2h_data_int_changed(self, enable):
        self.actions.en_d2h_data_int_changed.emit(enable)

    def en_dma_setup_int_changed(self, enable):
        self.actions.en_dma_setup_int_changed.emit(enable)

    def en_set_device_bits_int_changed(self, enable):
        self.actions.en_set_device_bits_int_changed.emit(enable)

    def sata_reset_checkbox_changed(self, enable):
        self.actions.sata_reset.emit(enable)


    #Controller
    def enable_sata_reset(self, enable):
        self.sata_reset_checkbox.setChecked(enable)

    def enable_command_layer_reset_checkbox(self, enable):
        self.command_layer_reset_checkbox.setChecked(enable)

    def enable_hd_int(self, enable):
        self.en_hd_int.setChecked(enable)

    def enable_dma_activate_int(self, enable):
        self.en_dma_activate_int.setChecked(enable)

    def enable_d2h_reg_int(self, enable):
        self.en_d2h_reg_int.setChecked(enable)

    def enable_pio_setup_int(self, enable):
        self.en_pio_setup_int.setChecked(enable)

    def enable_d2h_data_int(self, enable):
        self.en_d2h_data_int.setChecked(enable)

    def enable_dma_setup_int(self, enable):
        self.en_dma_setup_int.setChecked(enable)

    def enable_set_device_bits_int(self, enable):
        self.en_set_device_bits_int.setChecked(enable)

    #Status
    def enable_platform_ready(self, enable):
        self.platform_ready.setChecked(enable)

    def enable_platform_error(self, enable):
        self.platform_error.setChecked(enable)

    def enable_sata_reset_active(self, enable):
        self.reset_active_checkbox.setChecked(enable)

    def enable_linkup(self, enable):
        self.linkup.setChecked(enable)

    def enable_command_layer_ready(self, enable):
        self.command_layer_ready.setChecked(enable)

    def enable_transport_layer_ready(self, enable):
        self.transport_layer_ready.setChecked(enable)

    def enable_link_layer_ready(self, enable):
        self.link_layer_ready.setChecked(enable)

    def enable_phy_layer_ready(self, enable):
        self.phy_layer_ready.setChecked(enable)

    def enable_sata_busy(self, enable):
        self.sata_busy.setChecked(enable)

    def enable_hard_drive_error(self, enable):
        self.hard_drive_error.setChecked(enable)

    def enable_pio_data_ready(self, enable):
        self.pio_data_ready.setChecked(enable)

    def enable_rx_comm_init_detect(self, enable):
        self.rx_comm_init_detect.setChecked(enable)

    def enable_rx_comm_wake_detect(self, enable):
        self.rx_comm_wake_detect.setChecked(enable)

    def enable_tx_comm_reset(self, enable):
        self.tx_comm_reset.setChecked(enable)

    def enable_tx_comm_wake(self, enable):
        self.tx_comm_wake.setChecked(enable)

    def enable_tx_oob_complete(self, enable):
        self.tx_oob_complete.setChecked(enable)

    #Hard Drive Status
    def enable_d2h_interrupt(self, enable):
        self.d2h_interrupt.setChecked(enable)

    def enable_d2h_notification(self, enable):
        self.d2h_notification.setChecked(enable)

    def enable_d2h_pmult(self, value):
        self.d2h_pmult.setText(str(value))

    def enable_d2h_status(self, value):
        if (value & 0x80) > 0:
            self.d2h_status_bsy.setChecked(True)
        else:
            self.d2h_status_bsy.setChecked(False)

        if (value & 0x40) > 0:
            self.d2h_status_drdy.setChecked(True)
        else:
            self.d2h_status_drdy.setChecked(False)

        if (value & 0x20) > 0:
            self.d2h_status_dwf.setChecked(True)
        else:
            self.d2h_status_dwf.setChecked(False)

        if (value & 0x10) > 0:
            self.d2h_status_dsc.setChecked(True)
        else:
            self.d2h_status_dsc.setChecked(False)

        if (value & 0x08) > 0:
            self.d2h_status_drq.setChecked(True)
        else:
            self.d2h_status_drq.setChecked(False)
                
        if (value & 0x04) > 0:
            self.d2h_status_corr.setChecked(True)
        else:
            self.d2h_status_corr.setChecked(False)

        if (value & 0x02) > 0:
            self.d2h_status_idx.setChecked(True)
        else:
            self.d2h_status_idx.setChecked(False)

        if (value & 0x01) > 0:
            self.d2h_status_err.setChecked(True)
        else:
            self.d2h_status_err.setChecked(False)

        self.d2h_status.setText("0x%02X" % value)

    def enable_d2h_error(self, value):
        if (value & 0x80) > 0:
            self.d2h_error_bbk.setChecked(True)
        else:
            self.d2h_error_bbk.setChecked(False)

        if (value & 0x40) > 0:
            self.d2h_error_unc.setChecked(True)
        else:
            self.d2h_error_unc.setChecked(False)

        if (value & 0x20) > 0:
            self.d2h_error_mc.setChecked(True)
        else:
            self.d2h_error_mc.setChecked(False)

        if (value & 0x10) > 0:
            self.d2h_error_idnf.setChecked(True)
        else:
            self.d2h_error_idnf.setChecked(False)

        if (value & 0x08) > 0:
            self.d2h_error_mcr.setChecked(True)
        else:
            self.d2h_error_mcr.setChecked(False)
                
        if (value & 0x04) > 0:
            self.d2h_error_abrt.setChecked(True)
        else:
            self.d2h_error_abrt.setChecked(False)

        if (value & 0x02) > 0:
            self.d2h_error_tk0nf.setChecked(True)
        else:
            self.d2h_error_tk0nf.setChecked(False)

        if (value & 0x01) > 0:
            self.d2h_error_amnf.setChecked(True)
        else:
            self.d2h_error_amnf.setChecked(False)


        self.d2h_error.setText(str(value))

    def set_oob_state(self, value):
        self.oob_state.setText(str(value))

    def set_debug_linkup_data(self, value):
        self.debug_linkup_data.setText("0x%08X" % value)

    def set_d2h_lba(self, value):
        self.d2h_lba.setText(str(value))

    def set_d2h_fis(self, value):
        if value == 0x27:
            self.d2h_fis.setText("H2D Register (0x%02X)" % value)
        elif value == 0x34:
            self.d2h_fis.setText("D2H Register (0x%02X)" % value)
        elif value == 0x39:
            self.d2h_fis.setText("DMA Activate (0x%02X)" % value)
        elif value == 0x41:
            self.d2h_fis.setText("DMA Setup (0x%02X)" % value)
        elif value == 0x46:
            self.d2h_fis.setText("Data (0x%02X)" % value)
        elif value == 0x58:
            self.d2h_fis.setText("BIST (0x%02X)" % value)
        elif value == 0x51:
            self.d2h_fis.setText("PIO Setup (0x%02X)" % value)
        elif value == 0xA1:
            self.d2h_fis.setText("Set Device Bits (0x%02X)" % value)
        else:
            self.d2h_fis.setText("Unknown FIS (0x%02X)" % value)

    def send_command(self):
        index = self.command_combo.currentIndex()
        command = 0
        if index == 0:
            command = 0x00 
        #elif index == 1:
        #    command = 0xB1
        #    self.actions.send_hard_drive_features.emit(0xC2)
        elif index == 1:
            command = 0x27
        elif index == 2:
            command = 0x08
        elif index == 3:
            command = 0xE3
        else:
            return
        self.actions.send_hard_drive_command.emit(command)
        self.actions.sata_refresh.emit()


