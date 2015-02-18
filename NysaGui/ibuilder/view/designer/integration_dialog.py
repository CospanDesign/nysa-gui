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


__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from functools import partial



class IntegrationDialog(QDialog):

    def __init__(self, name, full_connected_list, connected_list, parent = None):
        super (IntegrationDialog, self).__init__(parent)
        self.integration_table = QTableWidget()

        self.name = name
        self.full_connected_list = full_connected_list
        self.connected_list = connected_list
        self.add_item = QPushButton("Add")
        self.add_item.clicked.connect(self.add_item_clicked)

        self.selector = QComboBox()
        self.selector.addItems(self.full_connected_list)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(self.name))
        hl = QHBoxLayout()
        hl.addWidget(self.selector)
        hl.addWidget(self.add_item)
        layout.addLayout(hl)

        layout.addWidget(self.integration_table)
        
        self.setLayout(layout)

        #Change every string to a qstring
        temp = list(self.connected_list)
        self.connected_list = []
        for data in temp:
            self.connected_list.append(QString(data))

        self.refresh_items()

    def refresh_items(self):
        self.integration_table.clear()
        self.integration_table.setColumnCount(2)
        self.integration_table.setHorizontalHeaderLabels(["Component", "Remove"])
        self.integration_table.horizontalHeader().setStretchLastSection(True)
        self.integration_table.setRowCount(len(self.connected_list))

        for i in range(len(self.connected_list)):
            self.integration_table.setCellWidget(i, 0, QLabel(self.connected_list[i]))

        self.integration_table.setCellWidget(len(self.connected_list), 0, self.selector)

        for i in range(len(self.connected_list)):
            remove = QPushButton("Remove")
            f = partial(self.remove_item_clicked, i)
            remove.clicked.connect(f)
            self.integration_table.setCellWidget(i, 1, remove)

    def add_item_clicked(self):
        current = self.selector.currentText()
        self.connected_list.append(current)
        self.refresh_items()

    def remove_item_clicked(self, index):
        current = self.integration_table.cellWidget(index, 0).text()
        print "current: %s" % current
        self.connected_list.remove(current)
        self.refresh_items()

    def get_new_integration_list(self):
        return self.connected_list

    @staticmethod
    def get_integration_list(name, full_connected_list, connected_list):
        dialog = IntegrationDialog(name, full_connected_list, connected_list)
        result = dialog.exec_()
        integration_list = dialog.get_new_integration_list()
        l = []
        for item in integration_list:
            l.append(str(item))
        return l
