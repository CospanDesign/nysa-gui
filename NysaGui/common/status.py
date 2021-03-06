#! /usr/bin/python

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

import os
import inspect

#from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)


white = '\033[0m'
gray = '\033[90m'
red = '\033[91m'
green = '\033[92m'
yellow = '\033[93m'
blue = '\033[94m'
purple = '\033[95m'
cyan = '\033[96m'

if os.name == "nt":
    white  = ''
    gray   = ''
    red    = ''
    green  = ''
    yellow = ''
    blue   = ''
    purple = ''
    cyan   = ''





StatusLevel = enum ('FATAL', 'ERROR', 'WARNING', 'INFO', 'IMPORTANT', 'DEBUG', 'VERBOSE')

_status_instance = None
_cl_status_instance = None

def Status(*args, **kw):
    global _status_instance
    if _status_instance is None:
        _status_instance = _Status(*args, **kw)
    return _status_instance

def ClStatus(*args, **kw):
    global _cl_status_instance
    if _cl_status_instance is None:
        _cl_status_instance = _ClStatus(*args, **kw)
    return _cl_status_instance

class _ClStatus(object):
    @staticmethod
    def is_command_line():
        return True

    def __init__(self):
        super(_ClStatus, self).__init__()
        self.level = StatusLevel.INFO

    def Verbose (self, text):
        if self.CheckLevel(StatusLevel.VERBOSE):
            self.status_output("Verbose", text, color = cyan)

    def Debug (self, text):
        if self.CheckLevel(StatusLevel.DEBUG):
            self.status_output("Debug", text, color = purple)

    def Info (self, text):
        if self.CheckLevel(StatusLevel.INFO):
            self.status_output("Info", text, color = white)

    def Important (self, text):
        if self.CheckLevel(StatusLevel.IMPORTANT):
            self.status_output("Important", text, color = blue)

    def Warning (self, text):
        if self.CheckLevel(StatusLevel.WARNING):
            self.status_output("Warning", text, color = yellow)

    def Error (self, text):
        if self.CheckLevel(StatusLevel.ERROR):
            self.status_output("Error", text, color=red)

    def Fatal (self, text):
        if self.CheckLevel(StatusLevel.FATAL):
            self.status_output("Fatal", text, color=red)

    def Print (self, text):
        self.status_output("", None, text)

    def PrintLine(self, text):
        self.status_output("", None, text)

    def status_output(self, level, text, color=white):
        
        function_name = str(inspect.stack()[2][3])
        #print "function_name: %s" % function_name
        if function_name == "<module>":
            function_name = str(inspect.stack()[2][1]).rpartition("./")[2] + ":main"

        class_name = None

        #print "\t%s" % str(dir(inspect.stack()[2][0].f_code))
        #print "\t%s" % str(inspect.stack()[2][0].f_code.co_name)
        #print "\t%s" % str(inspect.stack()[2][0].f_trace)
        #print "\t%s" % str(inspect.stack()[2][0].f_globals["__name__"])
        #print "\t%s" % str(inspect.stack()[2][0].f_globals.viewitems())
        #print "\t%s" % str(inspect.stack()[2][0].f_locals["__class__"])
        if "self" in inspect.stack()[2][0].f_locals.keys():
            #print "\t%s" % str(inspect.stack()[2][0].f_locals["self"])
            #print "\t%s" % str(dir(inspect.stack()[2][0].f_locals["self"]))
            
            class_name = str(inspect.stack()[2][0].f_locals["self"])
            while class_name.find(".") != -1:
                class_name = class_name.partition(".")[2]
            class_name = class_name.partition(" ")[0]

            class_name = class_name.strip("(")
            class_name = class_name.strip(")")

        if class_name is not None and (len(class_name) > 0) and (class_name.strip() != "<module>"):
            d = "%s:%s: " % (class_name, function_name)
        else:
            d = "%s: " % (function_name)

        text = d + text
        print "%s%s: %s%s" % (color, level, text, white)

    def set_level(self, level):
        self.level = level

    def GetLevel(self):
        return self.level

    def CheckLevel(self, requestLevel):
        if requestLevel == StatusLevel.FATAL:
            return True
        elif requestLevel is StatusLevel.VERBOSE:
            if  self.level == StatusLevel.VERBOSE:
                return True
        elif requestLevel is StatusLevel.DEBUG:
            if  self.level == StatusLevel.VERBOSE or \
                self.level == StatusLevel.DEBUG:
                return True
        elif requestLevel is StatusLevel.INFO:
            if self.level == StatusLevel.VERBOSE or  \
                self.level == StatusLevel.DEBUG or   \
                self.level == StatusLevel.INFO:
                return True
        elif requestLevel is StatusLevel.IMPORTANT:
            if self.level == StatusLevel.VERBOSE or  \
                self.level == StatusLevel.DEBUG or   \
                self.level == StatusLevel.INFO or    \
                self.level == StatusLevel.IMPORTANT:
                return True
        elif requestLevel is StatusLevel.WARNING:
            if self.level == StatusLevel.VERBOSE or  \
                self.level == StatusLevel.DEBUG or   \
                self.level == StatusLevel.INFO  or   \
                self.level == StatusLevel.IMPORTANT or \
                self.level == StatusLevel.WARNING:
                return True
        elif requestLevel is StatusLevel.ERROR:
            if self.level == StatusLevel.VERBOSE or  \
                self.level == StatusLevel.DEBUG or   \
                self.level == StatusLevel.INFO  or   \
                self.level == StatusLevel.IMPORTANT or \
                self.level == StatusLevel.WARNING or \
                self.level == StatusLevel.ERROR:
                return True
       
        return False

    def cl_status(level = 2, text = ""):
        #if not text.endswith("\n"):
        #    text = text + "\n"

        if level == 0:
            print "%sVerbose: %s%s" % (cyan, text, white)
        elif level == 1:
            print "%sDebug: %s%s" % (green, text, white)
        elif level == 2:
            print "%sInfo: %s%s" % (white, text, white)
        elif level == 3:
            print "%sImportant: %s%s" % (blue, text, white)
        elif level == 4:
            print "%sWarning: %s%s" % (yellow, text, white)
        elif level == 5:
            print "%sError: %s%s" % (red, text, white)
        elif level == 6:
            print "%sCritical: %s%s" % (red, text, white)
        else:
            print "Unknown Level (%d) Text: %s" % (level, text)



class _Status(QWidget):
    status_list = None
    mdl = None

    @staticmethod
    def is_command_line():
        return False

    def __init__(self):
        super (_Status, self).__init__()
        #QWidget.__init__(self)
        self.level = StatusLevel.INFO
        self.init_ui()
        self.main_thread_name = QThread.currentThread().objectName()
       
        #self.Verbose("Hello World!")

    def init_ui(self):
        self.setWindowTitle('Status')
       
        self.status_list = QTableView()
        header = ["Index", "Level", "Class", "Message"]
        self.mdl = StatusModel([[]], header, self)
        self.status_list.setModel(self.mdl)
        #self.setMinimumSize(400, 300)d
        #self.setMaximumHeight(200)
       
        #Hide the grids
        self.status_list.setShowGrid(False)
        self.status_list.setSelectionBehavior(QAbstractItemView.SelectRows)
       
        #Hide vertical header
        vh = self.status_list.verticalHeader()
        vh.setVisible(False)
        #Set horizontal header properties
        hh = self.status_list.horizontalHeader()
        hh.setStretchLastSection(True)
       
        #set column width to fit contents
        self.status_list.resizeColumnsToContents()
       
        layout = QVBoxLayout()
        layout.addWidget(self.status_list)
        self.setLayout(layout)
        #self.show()

    def Verbose (self, text):
        if self.CheckLevel(StatusLevel.VERBOSE):
            self.status_output("Verbose", text, fg = "White", bg="Blue")

    def Debug (self, text):
        if self.CheckLevel(StatusLevel.DEBUG):
            self.status_output("Debug", text, fg = "White", bg="Black")

    def Info (self, text):
        if self.CheckLevel(StatusLevel.INFO):
            self.status_output("Info", text, fg="Green", bg="Black")

    def Important (self, text):
        if self.CheckLevel(StatusLevel.IMPORTANT):
            self.status_output("Important:", text, fg="Blue", bg="Black")

    def Warning (self, text):
        if self.CheckLevel(StatusLevel.WARNING):
            self.status_output("Warning", text, fg="Yellow", bg="Black")

    def Error (self, text):
        if self.CheckLevel(StatusLevel.ERROR):
            self.status_output("Error", text, fg="Red", bg='White')

    def Fatal (self, text):
        if self.CheckLevel(StatusLevel.FATAL):
            self.status_output("Fatal", text, fg="Red", bg="Black")

    def Print (self, text):
        self.status_output("Extra", self, text, fg="Black", bg="White")

    def PrintLine(self, text):
        self.status_output("Extra", self, text, fg="Black", bg="White")

    def status_output(self, level, text, fg = None, bg = None):
        stack_info = inspect.stack()
        if QThread.currentThread().objectName() != self.main_thread_name:
            #Condition in which the status is updated from external thread
            QMetaObject.invokeMethod(self,
                                     "_status_output",
                                     Qt.QueuedConnection,
                                     Q_ARG(str, level),
                                     Q_ARG(str, text),
                                     Q_ARG(object, fg),
                                     Q_ARG(object, bg),
                                     Q_ARG(object, stack_info))
            return
        self._status_output(level, text, fg, bg, stack_info)
        
    @pyqtSlot(str, str, object, object, object)
    def _status_output(self, level, text, fg = None, bg = None, stack_info = None):
        pos = self.mdl.rowCount()
        #print "Position: %d" % pos
        self.mdl.insertRows(pos, 1)


        function_name = str(stack_info[2][3])
        if function_name == "<module>":
            function_name = str(stack_info[2][1]).rpartition("./")[2] + ":main"

        class_name = None

        d = None
        if "self" in stack_info[2][0].f_locals.keys():
            class_name = str(stack_info[2][0].f_locals["self"])
            while class_name.find(".") != -1:
                class_name = class_name.partition(".")[2]
            class_name = class_name.partition(" ")[0]

            class_name = class_name.strip("(")
            class_name = class_name.strip(")")

        if class_name is not None and (len(class_name) > 0) and (class_name.strip() != "<module>"):
            d = "%s:%s: " % (class_name, function_name)
        else:
            d = "%s: " % (function_name)

        f = str(stack_info[2][3])

        self.mdl.set_line_data([str(pos), level, d, text, fg, bg])
        self.status_list.resizeColumnsToContents()
        self.status_list.scrollToBottom()
        hh = self.status_list.horizontalHeader()
        hh.setStretchLastSection(True)

    def set_level(self, level):
        self.level = level

    def GetLevel(self):
        return self.level

    def CheckLevel(self, requestLevel):

        if requestLevel is StatusLevel.FATAL:
            return True

        elif requestLevel is StatusLevel.VERBOSE:
            if  self.level == StatusLevel.VERBOSE:
                return True

        elif requestLevel is StatusLevel.DEBUG:
            if  self.level == StatusLevel.VERBOSE or \
                self.level == StatusLevel.DEBUG:
                return True

        elif requestLevel is StatusLevel.INFO:
            if self.level == StatusLevel.VERBOSE or  \
                self.level == StatusLevel.DEBUG or   \
                self.level == StatusLevel.INFO:
                return True

        elif requestLevel is StatusLevel.IMPORTANT:
            if self.level == StatusLevel.VERBOSE or  \
                self.level == StatusLevel.DEBUG or   \
                self.level == StatusLevel.INFO  or   \
                self.level == StatusLevel.IMPORTANT:
                return True

        elif requestLevel is StatusLevel.WARNING:
            if self.level == StatusLevel.VERBOSE or  \
                self.level == StatusLevel.DEBUG or   \
                self.level == StatusLevel.INFO  or   \
                self.level == StatusLevel.IMPORTANT  or   \
                self.level == StatusLevel.WARNING:
                return True
        elif requestLevel is StatusLevel.ERROR:
            if self.level == StatusLevel.VERBOSE or  \
                self.level == StatusLevel.DEBUG or   \
                self.level == StatusLevel.INFO  or   \
                self.level == StatusLevel.IMPORTANT  or   \
                self.level == StatusLevel.WARNING or \
                self.level == StatusLevel.ERROR:
                return True

        return False

    def paint(self, event):
        self.QWidget.paint(self, event)

class StatusModel(QAbstractTableModel):
    def __init__(self, data_in = [[]], header_data=[], parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.array_data = []
        self.header_data = header_data
        self.brush = QBrush(Qt.gray)
 
    def rowCount(self, parent=None):
        return len(self.array_data)
 
    def columnCount(self, parent):
        return len(self.header_data)
 
    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
 
    def data(self, index, role):
      if role == Qt.ForegroundRole:
          return self.array_data[index.row()][4]

      if role == Qt.BackgroundRole:
          return QBrush(self.array_data[index.row()][5])

      if index.isValid() and role == Qt.DisplayRole:
          if index.column() < 4:
            return self.array_data[index.row()][index.column()]
 
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if col < 4:
                return self.header_data[col]
 
    def set_line_data(self, data):
        self.array_data.append([data[0], data[1], data[2], data[3], QColor(data[4]), QColor(data[5])])
 
    def insertRows(self, pos, rows, parent = QModelIndex()):
        self.beginInsertRows(parent, pos, pos + rows - 1) 
        self.endInsertRows()
        return True


