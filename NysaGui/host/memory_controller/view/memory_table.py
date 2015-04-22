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

ss = os.path.join(os.path.dirname(__file__), "stylesheet.css")
STYLE = open(ss, "r").read()



class TableModel(QtCore.QAbstractTableModel):
    def __init__(self):
        QtCore.QAbstractTableModel.__init__(self)
        self.items=['One','Two','Three','Four','Five','Six','Seven']
        self.headers = ["Address", "",  "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.items)
    def columnCount(self, index=QtCore.QModelIndex()):
        return 35

    def data(self, index, role):
        if not index.isValid() or not (0<=index.row()<len(self.items)):
            return QtCore.QVariant()

        item=str(self.items[index.row()])

        if role==QtCore.Qt.UserRole:
           return item
        if role==QtCore.Qt.DisplayRole:
           return item
        if role==QtCore.Qt.TextColorRole:
           return QtCore.QVariant(QtGui.QColor(QtCore.Qt.white))

    def headerData(self, column, orientation, role=QtCore.Qt.DisplayRole):
        if role!=QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        if orientation==QtCore.Qt.Horizontal:
            return QtCore.QVariant(self.headers[column])

class TableView(QtGui.QTableView):
    def __init__(self, parent=None):
        super(TableView, self).__init__(parent)
        #self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        myModel=TableModel()
        self.setModel(myModel)

        appStyle="""
        QTableView
        {
        background-color: black;
        gridline-color:black;
        color: black;
        selection-color: black;
        }
        QTableView::item
        {
        color: white;
        background:black;
        }
        QTableView::item:hover
        {
        color: black;
        background:#ffaa00;
        }
        QTableView::item:focus
        {
        color: black;
        background:#0063cd;
        }
        """
        self.setStyleSheet(appStyle)

class MemoryTable(QWidget):

    def __init__(self, memory = None):
        super (MemoryTable, self).__init__()
        self.mem = memory
        #self.mem_table = QTableWidget(32, 35)
        self.mem_table = TableView()
        #self.mem_table.setHorizontalHeaderLabels(["Address", "",  "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"])
        layout = QVBoxLayout()
        layout.addWidget(self.mem_table)
        model = self.mem_table.model()
        #self.mem_table.setStyleSheet(STYLE)
        self.setLayout(layout)



