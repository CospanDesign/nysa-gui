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

        self.pcie_rx_polarity_checkbox    = QCheckBox()
        self.pcie_rx_polarity_checkbox.clicked.connect(self.pcie_polarity_changed)
        self.pcie_reset_checkbox          = QCheckBox()
        self.pcie_reset_checkbox.clicked.connect(self.pcie_reset_changed)
        self.sata_reset_checkbox          = QCheckBox()
        self.sata_reset_checkbox.clicked.connect(self.sata_reset_changed)
        self.gtp_rx_pre_amp               = QComboBox()
        self.gtp_rx_pre_amp.addItems(["0", "1", "2", "3"])
        self.gtp_rx_pre_amp.setCurrentIndex(0)
        self.gtp_rx_pre_amp.currentIndexChanged.connect(self.gtp_rx_pre_amp_changed)
        self.gtp_tx_diff_swing            = QComboBox()
        self.gtp_tx_diff_swing.addItems(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"])
        self.gtp_tx_diff_swing.setCurrentIndex(0)
        self.gtp_tx_diff_swing.currentIndexChanged.connect(self.gtp_tx_diff_swing_changed)
        

        self.sata_pll_detect_k_checkbox   = QCheckBox()
        self.sata_pll_detect_k_checkbox.setEnabled(False)
        self.pcie_pll_detect_k_checkbox   = QCheckBox()
        self.pcie_pll_detect_k_checkbox.setEnabled(False)
        self.sata_reset_done_checkbox     = QCheckBox()
        self.sata_reset_done_checkbox.setEnabled(False)
        self.pcie_reset_done_checkbox     = QCheckBox()
        self.pcie_reset_done_checkbox.setEnabled(False)
        self.sata_dcm_pll_locked_checkbox = QCheckBox()
        self.sata_dcm_pll_locked_checkbox.setEnabled(False)
        self.pcie_dcm_pll_locked_checkbox = QCheckBox()
        self.pcie_dcm_pll_locked_checkbox.setEnabled(False)
        self.sata_rx_idle_checkbox        = QCheckBox()
        self.sata_rx_idle_checkbox.setEnabled(False)
        self.pcie_rx_idle_checkbox        = QCheckBox()
        self.pcie_rx_idle_checkbox.setEnabled(False)
        self.sata_tx_idle_checkbox        = QCheckBox()
        self.sata_tx_idle_checkbox.setEnabled(False)
        self.pcie_tx_idle_checkbox        = QCheckBox()
        self.pcie_tx_idle_checkbox.setEnabled(False)
        self.sata_lost_sync_checkbox      = QCheckBox()
        self.sata_lost_sync_checkbox.setEnabled(False)
        self.pcie_lost_sync_checkbox      = QCheckBox()
        self.pcie_lost_sync_checkbox.setEnabled(False)
        self.sata_rx_byte_aligned_checkbox = QCheckBox()
        self.sata_rx_byte_aligned_checkbox.setEnabled(False)
        self.pcie_rx_byte_aligned_checkbox = QCheckBox()
        self.pcie_rx_byte_aligned_checkbox.setEnabled(False)


        self.ref_clock_count = QLineEdit("NAN")
        self.ref_clock_count.setEnabled(False)

        self.ref_fst_clock_count = QLineEdit("NAN")
        self.ref_fst_clock_count.setEnabled(False)




        control_layout = QFormLayout()
        control_layout.addRow("GTPs", QLabel("Gigabit Transceivers"))
        control_layout.addRow("GTP Pre Amplifier", self.gtp_rx_pre_amp)
        control_layout.addRow("GTP Transmit Diff Swing", self.gtp_tx_diff_swing)

        control_layout.addRow("PCIE Reset", self.pcie_reset_checkbox)
        control_layout.addRow("PCIE Reset Done", self.pcie_reset_done_checkbox)
        control_layout.addRow("PCIE GTP PLL Locked", self.pcie_pll_detect_k_checkbox)
        control_layout.addRow("PCIE RX Polarity (positive)", self.pcie_rx_polarity_checkbox)
        control_layout.addRow("PCIE RX Idle", self.pcie_rx_idle_checkbox)
        control_layout.addRow("PCIE TX Idle", self.pcie_tx_idle_checkbox)
        control_layout.addRow("PCIE Lost Sync", self.pcie_lost_sync_checkbox)
        control_layout.addRow("PCIE Byte Aligned", self.pcie_rx_byte_aligned_checkbox)

        control_layout.addRow("SATA Reset", self.sata_reset_checkbox)
        control_layout.addRow("SATA Reset Done", self.sata_reset_done_checkbox)
        control_layout.addRow("SATA RX Idle", self.sata_rx_idle_checkbox)
        control_layout.addRow("SATA TX Idle", self.sata_tx_idle_checkbox)
        control_layout.addRow("SATA GTP PLL Locked", self.sata_pll_detect_k_checkbox)
        #control_layout.addRow("SATA Lost Sync", self.sata_lost_sync_checkbox)
        control_layout.addRow("SATA Byte Aligned", self.sata_rx_byte_aligned_checkbox)

        control_layout.addRow("PLLs", QLabel("Phase Lock Loops that generate clocks"))
        control_layout.addRow("SATA 300MHz/75MHz Locked", self.sata_dcm_pll_locked_checkbox)
        control_layout.addRow("PCIE 250MHz/62.5MHz Locked", self.pcie_dcm_pll_locked_checkbox)
        control_layout.addRow("75MHz Count", self.ref_clock_count)
        control_layout.addRow("300MHz Count", self.ref_fst_clock_count)


        layout = QVBoxLayout()
        layout.addWidget(self.refresh_button)

        layout.addLayout(control_layout)
        self.setLayout(layout)

    def refresh(self):
        self.status.Debug("Refresh")
        self.actions.artemis_refresh.emit()

    def set_pcie_rx_polarity(self, enable):
        self.pcie_rx_polarity_checkbox.setChecked(enable)

    def set_pcie_reset(self, enable):
        self.pcie_reset_checkbox.setChecked(enable)

    def set_sata_reset(self, enable):
        self.sata_reset_checkbox.setChecked(enable)

    def set_gtp_tx_diff_swing(self, index):
        self.gtp_tx_diff_swing.setCurrentIndex(index)

    def set_gtp_rx_preamp(self, index):
        self.gtp_rx_pre_amp.setCurrentIndex(index)

    def set_sata_gtp_pll_locked(self, enable):
        self.sata_pll_detect_k_checkbox.setChecked(enable)

    def set_pcie_gtp_pll_locked(self, enable):
        self.pcie_pll_detect_k_checkbox.setChecked(enable)

    def set_sata_reset_done(self, enable):
        self.sata_reset_done_checkbox.setChecked(enable)

    def set_pcie_reset_done(self, enable):
        self.pcie_reset_done_checkbox.setChecked(enable)

    def set_sata_dcm_pll_locked(self, enable):
        self.sata_dcm_pll_locked_checkbox.setChecked(enable)

    def set_pcie_dcm_pll_locked(self, enable):
        self.pcie_dcm_pll_locked_checkbox.setChecked(enable)

    def set_sata_rx_idle(self, enable):
        self.sata_rx_idle_checkbox.setChecked(enable)

    def set_pcie_rx_idle(self, enable):
        self.pcie_rx_idle_checkbox.setChecked(enable)

    def set_sata_tx_idle(self, enable):
        self.sata_tx_idle_checkbox.setChecked(enable)

    def set_pcie_tx_idle(self, enable):
        self.pcie_tx_idle_checkbox.setChecked(enable)

    def pcie_polarity_changed(self):
        c = (self.pcie_rx_polarity_checkbox.checkState() == 2)
        self.actions.pcie_rx_polarity.emit(c)

    def pcie_reset_changed(self):
        c = (self.pcie_reset_checkbox.checkState() == 2)
        self.actions.pcie_reset.emit(c)

    def sata_reset_changed(self):
        c = (self.sata_reset_checkbox.checkState() == 2)
        self.actions.sata_reset.emit(c)

    def gtp_rx_pre_amp_changed(self, value):
        value = int(str(value), 10)
        self.actions.gtp_preamp_changed.emit(value)

    def gtp_tx_diff_swing_changed(self, value):
        value = int(str(value), 10)
        self.actions.gtp_tx_swing_changed.emit(value)
        
    def set_sata_lost_sync(self, enable):
        self.sata_lost_sync_checkbox.setChecked(enable)

    def set_pcie_lost_sync(self, enable):
        self.pcie_lost_sync_checkbox.setChecked(enable)

    def set_sata_rx_byte_aligned(self, enable):
        self.sata_rx_byte_aligned_checkbox.setChecked(enable)

    def set_pcie_rx_byte_aligned(self, enable):
        self.pcie_rx_byte_aligned_checkbox.setChecked(enable)

    def set_ref_clock_count(self, count):
        #count = float(count)
        #Make into megahertz
        #count = count / 1000000
        self.ref_clock_count.setText(str(count))

    def set_ref_fst_clock_count(self, count):
        #count = float(count)
        #Make into megahertz
        #count = count / 1000000
        self.ref_fst_clock_count.setText(str(count))



