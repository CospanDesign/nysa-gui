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

class Configuration(QWidget):

    def __init__(self, actions, status):
        super (Configuration, self).__init__()
        self.status = status
        self.actions = actions
        layout = QFormLayout()
        name_layout = QHBoxLayout()
        self.project_name_line = QLineEdit()
        update_project_name_button = QPushButton("Update Project Name")
        update_project_name_button.clicked.connect(self.update_project_name_button)
        name_layout.addWidget(self.project_name_line)
        name_layout.addWidget(update_project_name_button)
        self.board_list = QComboBox()
        self.current_project_name = ""

        layout.addRow("project name", name_layout)
        layout.addRow("board select", self.board_list)
        layout.addRow("internal bindings", self.setup_internal_bind_widget())

        self.setLayout(layout)

    def setup_internal_bind_widget(self):
        layout = QVBoxLayout()
        self.bind_button = QPushButton("Connect")
        self.bind_button.clicked.connect(self.internal_bind_clicked)
        self.unbind_button = QPushButton("Disconnect")
        self.unbind_button.clicked.connect(self.internal_unbind_clicked)

        self.connected_signals = QTableView()
        self.internal_bind_model = InternalBindModel()
        self.connected_signals.setModel(self.internal_bind_model)
        self.connected_signals.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.connected_signals.horizontalHeader().setStretchLastSection(True)

        #XXX: Punt internal bind autimation till Rev 2.0 no time :( 
        #self.available_signals = QListWidget()
        #self.possible_signals = QListWidget()
        #XXX: This requires the user to manually enter in signals to bind,
        #   It is pretty lame but to implement it correctly would require a lot
        #   of time and I need to get Rev 1.0 out
        self.available_signals = QLineEdit()
        self.possible_signals = QLineEdit()

        signals_layout = QHBoxLayout()
        signals_layout.addWidget(self.available_signals)
        signals_layout.addWidget(self.bind_button)
        signals_layout.addWidget(self.possible_signals)

        layout.addLayout(signals_layout)
        layout.addWidget(self.connected_signals)
        layout.addWidget(self.unbind_button)
        return layout

    def internal_bind_clicked(self):
        #Error check
        to_signal = self.available_signals.text()
        from_signal = self.possible_signals.text()
        if len(to_signal) == 0:
            self.status.Error("\"to_signal\" must be specified, and cannot be left empty!")
            return

        if len(from_signal) == 0:
            self.status.Error("\"from_signal\" must be specified, and cannot be left empty!")
            return
        self.actions.internal_bind_connect.emit(to_signal, from_signal)

    def internal_unbind_clicked(self):
        #Error check
        selected_indexes = self.connected_signals.selectedIndexes()
        if len(selected_indexes) == 0:
            self.connected_signals.setSelection(QRect(0, 0, 2, 1), QItemSelectionModel.Rows | QItemSelectionModel.Select)
            self.status.Error("Please select a row to disconnect")
            return
        #print "selected indexes: %s" % str(selected_indexes)
        to_signal_index = selected_indexes[0]
        to_signal  = self.connected_signals.model().data(to_signal_index, role = Qt.DisplayRole)
        #print "to_signal: %s" % to_signal
        if len(to_signal) == 0:
            self.status.Error("\"to_signal\" must be specified, and cannot be left empty!")
            return
        self.actions.internal_bind_disconnect.emit(to_signal)

    def set_project_name(self, name):
        self.project_name_line.setText(name)
        self.current_project_name = name

    def get_project_name(self):
        return self.project_name_line.text()

    def populate_available_signals(self, signals):
        #self.available_signals.clear()
        #self.available_signals.addItems(signals)
        #XXX: Punt internal bind autimation till Rev 2.0 no time :( 
        pass

    def populate_signals_possible(self, signals):
        #self.possible_signals.clear()
        #self.possible_signals.addItems(signals)
        #XXX: Punt internal bind autimation till Rev 2.0 no time :( 
        pass

    def populate_connected_signals(self, signals):
        self.internal_bind_model.clear()
        for signal in signals:
            self.internal_bind_model.insert_line(signal, signals[signal])

    def set_board(self, board):
        index = self.board_list.findText(board, Qt.MatchExactly)
        self.board_list.setCurrentIndex(index)

    def populate_board_list(self, boards):
        self.board_list.clear()
        self.board_list.addItems(boards)

    def update_project_name_button(self):
        project_name = self.project_name_line.text()
        self.actions.update_project_name.emit(self.current_project_name, project_name)

class InternalBindModel(QAbstractTableModel):
    def __init__(self, header_data=["Signal To", "Signal From"], parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.array_data = []
        self.header_data = header_data
 
    def rowCount(self, parent=None):
        return len(self.array_data)
 
    def columnCount(self, parent):
        return len(self.header_data)
 
    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
 
    def data(self, index, role):
      if index.isValid() and role == Qt.DisplayRole:
          if index.column() < 2:
            return self.array_data[index.row()][index.column()]
 
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if col < 4:
                return self.header_data[col]
 
    def insert_line(self, to_signal, from_signal):
        self.array_data.append([to_signal, from_signal])
        self.beginInsertRows(QModelIndex(), 0, 0)
        self.endInsertRows()

    def clear(self):
        if self.rowCount() > 0:
            self.beginRemoveRows(QModelIndex(), 0, self.rowCount())
            self.endRemoveRows()
        self.array_data = []

        self.removeRows(0, self.rowCount())

