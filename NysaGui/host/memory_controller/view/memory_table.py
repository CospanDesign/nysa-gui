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


DEFAULT_ROW_COUNT = 40
DEFAULT_CACHE_BUFFER = 0

class MemCache(object):
    def __init__(self):
        super(MemCache, self).__init__()
        self.data = Array('B')
        self.start = 0
        self.position = 0
        self.mem_size = 0
        self.row_count = DEFAULT_ROW_COUNT
        self.cache_buffer = DEFAULT_CACHE_BUFFER
        self.busy = False
        for i in range(self.cache_size()):
            self.data.append(i)
            self.data.append(i)
            self.data.append(i)
            self.data.append(i)
            self.data.append(i)
            self.data.append(i)
            self.data.append(i)
            self.data.append(i)

    def cache_size(self):
        return self.row_count + self.cache_buffer

    def set_nysa(self, nysa):
        self.n = nysa

    def set_urn(self, urn):
        self.urn = urn
        self.mem_size = self.n.get_device_size(urn)
        self.mem_base = self.n.get_device_address(urn)
        self.position = self.mem_base
        self.start = -1
        #XXX: Debug
        self.invalidate()

    def set_cache_buffer(self, cache_buffer):
        self.cache_buffer = cache_buffer;
        self.invalidate()

    def set_row_count(self, row_count):
        self.row_count = row_count
        self.invalidate()
        
    def get_row_count(self):
        return self.row_count

    def get_position(self):
        return self.position

    def move_up(self, amount = 1):
        #print "move up"
        self.position -= amount
        self.check()

    def get_start_addr(self):
        return self.mem_base

    def move_down(self, amount = 1):
        #Check to see if the user is at the end of memory
        #print "move down"
        position = amount + self.position
        if (position - self.cache_buffer + self.cache_size()) >= (self.mem_base + self.mem_size):
            self.position = self.mem_base + (self.mem_size) - (self.cache_size())
        else:
            self.position = position
        self.check()

    def check(self):
        #Check if we need to get more data from the memory
        #print "checking..."
        #print "s: %d p: %d cb: %d cs: %d" % (self.start, self.position, self.cache_buffer, self.cache_size())
        if self.position < self.mem_base:
            self.position = self.mem_base
            self.invalidate()
            return

        if self.position > (self.mem_size) + self.mem_base - self.cache_size():
            self.position = (self.mem_size) + self.mem_base - self.cache_size()
            print "possible overshoot, position: 0x%08X" % self.position
            self.invalidate()
            return

        if (self.position - self.cache_buffer + self.row_count) > (self.start + self.cache_size()):
            print "Need to get more data"
            print "Position - cache buffer > start + cache_size"
            print "\t0x%08X - 0x%02X + 0x%02X > 0x%08X + 0x%02X" % (self.position, self.cache_buffer, self.row_count, self.start, self.cache_size())
            print "\t0x%08X > 0x%08X" % ((self.position - self.cache_buffer + self.row_count), self.start + self.cache_size())
            self.invalidate()
            return

        if (self.position - self.cache_buffer) < self.start:
            if self.start == 0:
                return
            print "Need to get more data,"
            self.invalidate()
            return

        return

    def invalidate(self):
        #Get more data from memory
        print "in invalidate"
        start = self.start
        if (self.position - self.cache_buffer) < self.mem_base:
            #check if we are at the beginning
            start = self.mem_base

        elif (self.position - self.cache_buffer + self.cache_size()) >= (self.mem_base + self.mem_size):
            print "we are close to the  end..."
            start = (self.mem_base + self.mem_size) - self.cache_size() + self.cache_buffer
            self.position = (self.mem_base + self.mem_size) - self.cache_size()
        else:
            start = self.position - self.cache_buffer

        #if start != self.start:
        print "update cache"
        print "start: 0x%08X" % start
        self.busy = True
        self.data = self.n.read_memory(start, self.cache_size())
        print "length of data read: %d" % len(self.data)
        print "Length of cache: %d" % self.cache_size()
        self.start = start
        self.busy = False

    def get_data(self, row, column):
        position = self.position - self.start + row
        #print "start: %d curr pos: %d row: %d column: %d: position: %d" % (self.start, self.position, row, column, position)
        #print "\tData Position: %d" % ((self.position * 4) + column)
        if self.busy:
            return "Loading..."
        try:
            return self.data[(position * 4) + column]
        except:
            return "??"

    def is_busy(self):
        return self.busy

    def at_end(self):
        if self.position == (self.mem_base + self.mem_size) - self.cache_size():
            return True
        return False

class TableModel(QtCore.QAbstractTableModel):
    def __init__(self):
        QtCore.QAbstractTableModel.__init__(self)
        self.mem_cache = MemCache()
        self.headers = ["Address", "",  "0", "1", "2", "3", "", "0", "1", "2", "3"]

    def rowCount(self, parent=QtCore.QModelIndex()):
        return self.mem_cache.get_row_count()

    def columnCount(self, index=QtCore.QModelIndex()):
        return len(self.headers)

    def set_nysa(self, nysa):
        self.n = nysa
        self.mem_cache.set_nysa(self.n)

    def set_urn(self, urn):
        self.urn = urn
        if self.n is None:
            print "Nysa is not set!"
        self.mem_cache.set_urn(urn)

    def data(self, index, role):
        if not index.isValid() or not (0<=index.row()<self.mem_cache.get_row_count()):
            return QtCore.QVariant()

        #item=str(self.items[index.row()])
        #if role==QtCore.Qt.UserRole:
        #    return item
        if role==QtCore.Qt.DisplayRole:
            if index.column() == 0:
                value = QtCore.QString("%08X" % (self.mem_cache.get_position() + index.row()))
                return QtCore.QVariant(value)
            if index.column() == 1:
                return QtCore.QVariant()
            if index.column() == 6:
                return QtCore.QVariant()
            if index.column() > 1 and index.column() < 6:
                value = self.mem_cache.get_data(index.row(), index.column() - 2)
                if isinstance(value, str):
                    return value
                return str("%02X" % value)
            else:
                value = self.mem_cache.get_data(index.row(), index.column() - 7)
                if isinstance(value, str):
                    return value
                return chr(value)


        if role==QtCore.Qt.TextColorRole:
            return QtCore.QVariant(QtGui.QColor(QtCore.Qt.white))

    def headerData(self, column, orientation, role=QtCore.Qt.DisplayRole):
        if role!=QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        if orientation==QtCore.Qt.Horizontal:
            return QtCore.QVariant(self.headers[column])

    def set_size(self, size):
        self.row_count = size

    def invalidate(self):
        self.mem_cache.invalidate()

    def move_down(self, amount = 1):
        self.mem_cache.move_down(amount)

    def move_up(self, amount = 1):
        self.mem_cache.move_up(amount)

    def is_busy(self):
        return self.mem_cache.is_busy()

    def get_position(self):
        return self.mem_cache.get_position()

    def get_start_addr(self):
        return self.mem_cache.get_start_addr()

    def at_end(self):
        return self.mem_cache.at_end()


class TableView(QtGui.QTableView):
    INITIAL_POS_MOVE_DELAY = 500
    #POS_MOVE_DELAY = 100
    POS_MOVE_DELAY = 25

    def __init__(self, parent=None):
        super(TableView, self).__init__(parent)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.setStyleSheet(STYLE)

        self.setAlternatingRowColors(True)
        myModel=TableModel()
        self.setModel(myModel)
        self.vscroll = self.verticalScrollBar()
        self.timer_id = 0
        self.timer_start = True
        self.vscroll.sliderReleased.connect(self.slider_released)

    def set_nysa(self, nysa):
        self.model().set_nysa(nysa)

    def set_urn(self, urn):
        self.model().set_urn(urn)
        self.reset()

    def set_size(self, size):
        self.model().set_size(size)
        self.reset()

    def invalidate(self):
        self.model().invalidate()
        self.reset()

    def timerEvent(self, timer_event):
        if timer_event.timerId() == self.timer_id:
            #print "Timer Fired!"
            if self.vscroll.value() == self.vscroll.maximum():
                #print "Moving Down"
                if self.model().at_end():
                    print "at end"
                    self.killTimer(self.timer_id)
                    self.timer_start = True
                    return

                if self.timer_start:
                    self.killTimer(self.timer_id)
                    self.timer_id = self.startTimer(self.POS_MOVE_DELAY)
                    self.timer_start = False

                if not self.model().is_busy():
                    self.model().move_down()
                    self.reset()
                else:
                    print "Busy"

            elif self.vscroll.value() == self.vscroll.minimum():
                #print "Moving Up"
                if self.model().get_position() <= self.model().get_start_addr():
                    self.killTimer(self.timer_id)
                    self.timer_start = True
                    return

                if self.timer_start:
                    self.killTimer(self.timer_id)
                    self.timer_id = self.startTimer(self.POS_MOVE_DELAY)
                    self.timer_start = False

                if not self.model().is_busy():
                    self.model().move_up()
                    self.reset()
                else:
                    print "Busy"

            else:
                print "killing timer"
                self.killTimer(self.timer_id)



    def slider_released(self):
        self.timer_start = True
        if self.timer_id != 0:
            print "Killing timer"
            self.killTimer(self.timer_id)
            self.timer_id = 0

    def verticalScrollbarValueChanged(self, value):
        #print "Value: %d" % value
        #print "Maximum: %d" % self.vscroll.maximum()
        #print "Minimum: %d" % self.vscroll.minimum()
        super(TableView, self).verticalScrollbarValueChanged(value)
        if value == self.vscroll.maximum():
            if self.model().at_end():
                print "at end"
                if self.timer_id != 0:
                    self.killTimer(self.timer_id)
                    self.timer_start = True
                return

            print "Start timer..."
            if self.timer_id == 0:
                self.timer_id = self.startTimer(self.INITIAL_POS_MOVE_DELAY)
                self.timer_start = True
            print "timer id: %d" % self.timer_id

        elif value == self.vscroll.minimum():
            if self.model().get_position() <= self.model().get_start_addr():
                if self.timer_id != 0:
                    self.killTimer(self.timer_id)
                    self.timer_start = True
                return
            #self.model().move_up()
            print "Start timer..."
            if self.timer_id == 0:
                self.timer_id = self.startTimer(self.INITIAL_POS_MOVE_DELAY)
                self.timer_start = True
            print "timer id: %d" % self.timer_id
        else:
            if self.timer_id != 0:
                self.killTimer(self.timer_id)
                self.timer_id = 0


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

    def invalidate(self):
        self.mem_table.invalidate()


