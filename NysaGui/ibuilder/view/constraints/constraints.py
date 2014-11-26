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
import json

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from signal_tree_table import SignalTreeTableModel
from constraint_tree_table import ConstraintTreeTableModel

class Constraints(QWidget):

    def __init__(self, actions, status, controller = None):
        super (Constraints, self).__init__()
        self.status = status
        self.actions = actions
        layout = QVBoxLayout()
        self.controller = controller
        self.signal_table = None
        self.pin_table = None
        self.connection_table = None
        self.connect_callback = None
        self.disconnect_callback = None
        #self.initialize_view()

    def initialize_view(self):
        layout = QVBoxLayout()

        unconnected_layout = QVBoxLayout()
        pin_layout = QVBoxLayout()

        splitter = QSplitter(Qt.Horizontal)
        connect = QPushButton("Connect")
        connect.clicked.connect(self.signal_connect)

        unconnected_panel = QWidget(self)
        pin_panel = QWidget(self)

        #Add the signal table to the unconnected layout
        self.signal_table = SignalTable(self.controller)
        self.connection_table = ConnectionTable(self.controller)
        self.create_pin_table()

        unconnected_layout.addWidget(self.signal_table)
        unconnected_panel.setLayout(unconnected_layout)

        pin_layout.addWidget(self.pin_table)
        pin_panel.setLayout(pin_layout)

        splitter.addWidget(unconnected_panel)
        splitter.addWidget(connect)
        splitter.addWidget(pin_panel)

        layout.addWidget(splitter)
        layout.addWidget(self.connection_table)
        self.setLayout(layout)
        #self.show()

    def set_connect_callback(self, connect):
        self.connect_callback = connect

    def set_disconnect_callback(self, disconnect):
        self.disconnect_callback = disconnect

    def set_controller(self, controller):
        self.controller = controller

    def clear_all(self):
        self.signal_table.clear()

        row_count = self.pin_model.rowCount()
        for i in range(row_count):
            self.pin_model.removeRow(0)
        self.connection_table.clear()

    def refresh_tables(self):
        self.controller.refresh_constraint_editor()

    def create_pin_table(self):
        self.pin_table = QTableView()
        self.pin_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.pin_table.setShowGrid(True)

        header = ["Pin Name"]

        self.pin_model = ConstraintModel([[]], header_data = header, parent = self)
        self.pin_table.setModel(self.pin_model)

        #Show the grids
        self.pin_table.setShowGrid(True)

        #Vertical tab settings
        vh = self.pin_table.verticalHeader()
        vh.setVisible(True)

        #Set horizontal header properties
        hh = self.pin_table.horizontalHeader()
        hh.setStretchLastSection(True)

    def add_signal(self, color, module_name, name, signal_range, direction, used_list = []):
        self.signal_table.add_signal(color, module_name, name, signal_range, direction, used_list)

    def remove_signal(self, module_name, port):
        self.signal_table.remove_signal(module_name, port)
 
    def add_pin(self, pin_name):
        pos = self.pin_model.rowCount()
        self.status.Debug("Adding Pin")
        self.pin_model.insertRows(pos, 1)
        self.pin_model.set_line_data([pin_name])

    def remove_pin(self, pin_name):
        pos = self.pin_model.find_pos([pin_name])
        if pos != -1:
            self.status.Debug("Pin Table: Remove Position: %d" % pos)
            success = self.pin_model.removeRow(pos)
            if success:
                self.status.Debug("Removed Signal")
 
    def add_connection(self, color, module_name, port, direction, pin_name, index = None):
        #print "Adding Connection: %s.%s" % (module_name, port)
        self.connection_table.add_connection(color, module_name, port, index, direction, pin_name)

    def remove_connection(self, module_name, port, index=None):
        self.connection_table.remove_connection(module_name, port, index)

    def notify_connection_delete(self, row_data):
        print "Disconnect Row Data: %s" % str(row_data)
        self.add_signal(row_data[0], row_data[1], row_data[2])
        self.add_pin(row_data[3])
        self.remove_connection(row_data[0], row_data[1])
        if self.disconnect_callback is not None:
            self.disconnect_callback(row_data[0], row_data[1], row_data[2], row_data[3])

    def signal_connect(self):
        print "Connect"
        signal_index_list = self.signal_table.selectedIndexes()
        pin_index_list = self.pin_table.selectedIndexes()
        if len(signal_index_list) == 0:
            self.status.Info("No signal is selected")
            return

        if len(pin_index_list) == 0:
            self.status.Info("No pin is selected")
            return

        #XXX: Only grab the first row
        signal_index = signal_index_list[-1]
        for signal in signal_index_list:
            print "Signal Location: %d, %d" % (signal.row(), signal.column())

        #print "signal location: %d, %d" % (signal_index.row(), signal_index.column())
        pin_row = pin_index_list[0].row()
        signal = self.signal_table.get_signal(signal_index)
        pin_data = self.pin_model.get_row_data(pin_row)

        #print "signal: %s" % str(signal)
        #print "pin_data: %s" % str(pin_data)

        module_name = signal[0]
        signal_name = signal[1]
        index = None
        if signal[2] != "None":
            index = int(signal[2])
        direction = signal[3]
        loc = pin_data[0]
        self.controller.connect_signal(module_name, signal_name, direction, index, loc)

        #print "Connection: %s" % str(connection)
        #self.status.Info("Connect: %s" % str(connection))
 
class ConstraintModel(QAbstractTableModel):
    def __init__(self, data_in = [[]], header_data=[], parent=None, *args):
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
        if index.isValid():
            if role == Qt.DisplayRole:
                return self.array_data[index.row()][index.column()]

    def find_pos(self, data):
        for i in range (len(self.array_data)):
            match = True
            for j in range (len(data)):
                #print "Comparing: %s - %s" % (self.array_data[i][j], data[j])
                if self.array_data[i][j] != data[j]:
                    match = False
                    break
            if match == True:
                #print "Found at %d!" % i
                return i
        return -1

    def get_row_data(self, row):
        return self.array_data[row]

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header_data[col]

    def set_line_data(self, data):
        self.array_data.append(data)

    def removeRow(self, pos, parent = QModelIndex()):
        if pos > len(self.array_data):
            return False
        self.beginRemoveRows(parent, pos, pos)
        val = self.array_data[pos]
        self.array_data.remove(val)
        self.endRemoveRows()
        return True

    def insertRows(self, pos, rows, parent = QModelIndex()):
        self.beginInsertRows(parent, pos, pos + rows - 1) 
        self.endInsertRows()
        return True


class SignalTable(QTreeView):

    def __init__(self, controller, parent=None):
        super(SignalTable, self).__init__(parent)
        self.setSelectionBehavior(QAbstractItemView.SelectRows |
                                  QAbstractItemView.SingleSelection)
        self.setUniformRowHeights(True)
        self.m = SignalTreeTableModel(controller, self)
        #A tree of two depth to allow users to select isolate modules
        self.setModel(self.m)
        self.connect(self, SIGNAL("activated(QModelIndex)"), self.activated)

        self.expand(self.rootIndex())

    def add_signal(self, color, module_name, name, signal_range, direction, used_list = []):
        #print "add signal: %s" % str(used_list)
        if len(used_list) > 0:
            #print "used list: %s" % str(used_list)
            pass
        #fields = [module_name, name, signal_range, direction]
        self.m.addRecord(color, module_name, name, signal_range, direction, used_list = used_list)

    def remove_signal(self, module_name, name, index=-1):
        self.m.removeRecord(module_name, name)

    def get_signal(self, index):
        return self.m.asRecord(index)

    def activated(self, index):
        print "Actived: %d, %d" % (index.row(), index.column())
        self.emit(SIGNAL("activated"), self.model().asRecord(index))

    def clear(self):
        self.m.clear()

    def selectionChanged(self, a, b):
        print "Selection Changed"
        super (SignalTable, self).selectionChanged(a, b)


class ConnectionTable(QTreeView):

    def __init__(self, controller, parent = None):
        super(ConnectionTable, self).__init__(parent)
        #self.setSelectionBehavior(QAbstractItemView.SelectRows | 
        #                          QAbstractItemView.SingleSelection)
        #self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setUniformRowHeights(True)
        self.m = ConstraintTreeTableModel(controller, self)
        self.setModel(self.m)
        self.connect(self, SIGNAL("activated(QModelIndex)"), self.activated)
        self.connect(self, SIGNAL("pressed(QModelIndex)"), self.pressed)

    def add_connection(self, color, module_name, name, index, direction, constraint_name):
        return self.m.addRecord(color, module_name, name, index, direction, constraint_name)

    def remove_connection(self, module_name, name, index = None):
        return self.m.removeRecord(module_name, name, index)

    def activated(self, index):
        print "Actived: %d, %d" % (index.row(), index.column())
        self.emit(SIGNAL("activated"), self.model().asRecord(index))

    def pressed(self, index):
        print "Pressed: %d, %d" % (index.row(), index.column())
        self.m.check_pressed(index)

    def clear(self):
        self.m.clear()

