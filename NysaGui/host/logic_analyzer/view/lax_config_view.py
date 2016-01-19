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
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QPushButton

from PyQt4 import QtCore

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir))


#from control_view import ControlView
direction_ss = os.path.join(os.path.dirname(__file__), "stylesheet.css")


INDEX_POS          = 0
EN_POS             = 1
TRIGGER_POL_POS    = 2

class LaxConfigWidget(QWidget):

    def __init__(self, count = 32, actions = None):
        super (LaxConfigWidget, self).__init__()
        self.actions = actions
        layout = QGridLayout()
        #status_layout = QVBoxLayout

        self.enable_buttons = []
        self.trigger_pol_values = []

        style = open(direction_ss, "r").read()

        layout.addWidget(QLabel("Index"             ), 0, INDEX_POS         , QtCore.Qt.AlignCenter)
        layout.addWidget(QLabel("Enable"            ), 0, EN_POS            , QtCore.Qt.AlignCenter)
        layout.addWidget(QLabel("Trigger on 1 or 0" ), 0, TRIGGER_POL_POS   , QtCore.Qt.AlignCenter)

        for i in range (0, count):
            #Index
            ilabel = QLabel("%d" % i)
            #ilabel.setObjectName("index_label")
            ilabel.setStyleSheet(style)

            #Enable
            en_btn = QPushButton("Disable")
            en_btn.setObjectName("enable_button")
            self.enable_buttons.append(en_btn)
            en_btn.setStyleSheet(style)
            en_btn.setCheckable(True)

            #Trigger Values
            trigger_pol_btn = QPushButton("0")
            trigger_pol_btn.setObjectName("trigger_button")
            self.trigger_pol_values.append(trigger_pol_btn)
            trigger_pol_btn.setStyleSheet(style)
            trigger_pol_btn.setCheckable(True)

            #Connect callbacks
            en_btn.clicked.connect(partial(self.enable_clicked, i))
            trigger_pol_btn.clicked.connect(partial(self.trigger_pol_clicked, i))

            #Add to layout
            #Index
            layout.addWidget(ilabel         , i + 1 , INDEX_POS       , QtCore.Qt.AlignCenter)
            layout.addWidget(en_btn         , i + 1 , EN_POS          , QtCore.Qt.AlignCenter)
            layout.addWidget(trigger_pol_btn, i + 1 , TRIGGER_POL_POS , QtCore.Qt.AlignCenter)

            layout.setRowStretch(i + 1, count)
            layout.setRowMinimumHeight(i + 1, count)

        #self.cv = ControlView(self.actions)

        #layout.addWidget(self.cv, 0, STATUS_POS, count, 1)
        self.setLayout(layout)

    def enable_clicked(self, index):
        self.enable_changed(index)
        btn = self.enable_buttons[index]
        self.actions.trigger_en_changed.emit()

    def enable_changed(self, index):
        btn = self.enable_buttons[index]
        if btn.isChecked():
            btn.setText("Enable")
        else:
            btn.setText("Disable")

    def trigger_pol_clicked(self, index):
        self.trigger_pol_changed(index)
        btn = self.trigger_pol_values[index]
        self.actions.trigger_pol_changed.emit()

    def trigger_pol_changed(self, index):
        btn = self.trigger_pol_values[index]
        if btn.isChecked():
            btn.setText("1")
        else:
            btn.setText("0")

    def update_all_enable(self, value):
        for i in range(len(self.enable_buttons)):
            reg = self.enable_buttons[i]
            if ((value & (1 << i)) != 0):
                reg.setChecked(True)
            else:
                reg.setChecked(False)
            self.enable_changed(i)

    def update_trigger_polarity(self, value):
        for i in range(len(self.trigger_pol_values)):
            btn = self.trigger_pol_values[i]
            if (value & (1 << i)) > 0:
                btn.setChecked(True)
            else:
                btn.setChecked(False)
            self.trigger_pol_changed(i)

    def get_trigger_polarity(self):
        trigger_polarity = 0
        for i in range(len(self.trigger_pol_values)):
            btn = self.trigger_pol_values[i]

            if btn.isChecked():
                trigger_polarity |= (1 << i)

        return trigger_polarity

    def get_trigger_enable(self):
        trigger_enable = 0
        for i in range(len(self.enable_buttons)):
            btn = self.enable_buttons[i]
            if btn.isChecked():
                trigger_enable |= (1 << i)

        return trigger_enable
