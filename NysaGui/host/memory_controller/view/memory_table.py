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


__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QTableWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtCore import QAbstractTableModel
from PyQt4.QtGui import QTableView
from PyQt4 import QtCore
from PyQt4 import QtGui
from array import array as Array

ss = os.path.join(os.path.dirname(__file__), "stylesheet.css")
STYLE = open(ss, "r").read()


DEFAULT_ROW_COUNT = 10
SIZE_DIVIDER = 2

class MemCache(object):
    def __init__(self):
        super(MemCache, self).__init__()
        self.data = Array('B')
        self.start = 0
        self.position = 0
        self.mem_size = 0
        self.cache_size = DEFAULT_ROW_COUNT * SIZE_DIVIDER

    def set_nysa(self, nysa):
        self.n = nysa

    def set_urn(self, urn):
        self.urn = urn
        self.mem_size = self.n.get_device_size(urn)
        self.start = self.n.get_device_address(urn)
        self.position = self.start
        self.invalidate()

    def get_row_count(self):
        return self.cache_size / SIZE_DIVIDER

    def get_position(self):
        return self.position

    def move_up(self, amount = 1):
        if (self.position + self.cache_size / DIVIDER) > (self.start + self.cache_size)
            self.position = self.start

    def move_down(self, amount = 1):
        if self.position + amount > 

    def check(self):
        #Check if we need to get more data from the memory
        if self.position < self.start:
            print "Need to get more data"

        if (self.position + self.cache_size / DIVIDER) > (self.start + self.cache_size)
            print "Need to get more data"

    def invalidate(self):
        #Get more data from memory

class TableModel(QtCore.QAbstractTableModel):
    def __init__(self):
        QtCore.QAbstractTableModel.__init__(self)
        self.items=['One','Two','Three','Four','Five','Six','Seven', "eight", "nine", "ten"]
        self.mem_cache = MemCache()

        self.mem_cache = {}
        self.mem_cache["size"] = DEFAULT_ROW_COUNT * 2
        self.mem_cache["start"] = 0
        self.mem_cache["position"] = 0
        self.mem_cache["data"] = Array('B')

        self.headers = ["Address", "",  "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]
        self.base = 0
        self.n = None
        self.urn = None
        self.row_count = self.mem_cache["size"] / 2
        for i in range(self.row):
            self.mem_cache["data"].append(0x00)
            self.mem_cache["data"].append(0x00)
            self.mem_cache["data"].append(0x00)
            self.mem_cache["data"].append(0x00)
            self.mem_cache["data"].append(0x00)
            self.mem_cache["data"].append(0x00)
            self.mem_cache["data"].append(0x00)
            self.mem_cache["data"].append(0x00)

        self.size = 0

    def rowCount(self, parent=QtCore.QModelIndex()):
        return self.row_count

    def columnCount(self, index=QtCore.QModelIndex()):
        return len(self.headers)

    def set_nysa(self, nysa):
        self.n = nysa

    def set_urn(self, urn):
        self.urn = urn
        if self.n is None:
            print "Nysa is not set!"
        self.base = self.n.get_device_address(self.urn)
        self.size = self.n.get_device_size(self.urn)

    def data(self, index, role):
        position = self.mem_cache["position"]
        if not index.isValid() or not (0<=index.row()<len(self.items)):
            return QtCore.QVariant()

        item=str(self.items[index.row()])
        if role==QtCore.Qt.UserRole:
            return item
        if role==QtCore.Qt.DisplayRole:
            if index.column() == 0:
                value = QtCore.QString("%08X" % (position + index.row()))
                return QtCore.QVariant(value)
            if index.column() == 1:
                return QtCore.QVariant()
            if index.column() == 18:
                return QtCore.QVariant()
            return item

        if role==QtCore.Qt.TextColorRole:
            return QtCore.QVariant(QtGui.QColor(QtCore.Qt.white))

    def headerData(self, column, orientation, role=QtCore.Qt.DisplayRole):
        if role!=QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        if orientation==QtCore.Qt.Horizontal:
            return QtCore.QVariant(self.headers[column])

    def set_size(self, size):
        self.row_count = size
        self.mem_cache["size"] = size

class TableView(QtGui.QTableView):
    def __init__(self, parent=None):
        super(TableView, self).__init__(parent)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.setStyleSheet(STYLE)

        self.setAlternatingRowColors(True)
        myModel=TableModel()
        self.setModel(myModel)

    def set_nysa(self, nysa):
        self.model().set_nysa(nysa)

    def set_urn(self, urn):
        self.model().set_urn(urn)
        self.reset()

    def set_size(self, size):
        self.model().set_size(size)
        self.reset()

class MemoryTable(QWidget):

    def __init__(self):
        super (MemoryTable, self).__init__()
        self.mem_table = TableView()
        layout = QVBoxLayout()
        layout.addWidget(self.mem_table)
        model = self.mem_table.model()
        self.setLayout(layout)

    def set_nysa(self, nysa):
        self.mem_table.set_nysa(nysa)

    def set_urn(self, urn):
        self.mem_table.set_urn(urn)

    def set_size(self, size):
        self.mem_table.set_size(size)


