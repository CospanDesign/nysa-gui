# -*- coding: utf-8 *-*

#Distributed under the MIT licesnse.
#Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#of the Software, and to permit persons to whom the Software is furnished to do
#so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import os
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from xmsgs_tree_model import XmsgsTreeModel

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

BUILDER_RESULT = enum ('PASS', 'PASS_WITH_WARNINGS', 'ERROR', 'BUSY', 'READY', 'UNKNOWN')

class Xmsgs(QWidget):
    
    def __init__(self, status):
        QWidget.__init__(self)
        self.setWindowTitle('Xilinx Builder Messages')

        self.xmsgs = XmsgsTreeView(self, status)
        #self.xmsgs = XmsgsTreeModel()

        #self.xmsgs.setShowGrid(False)
        #self.xmsgs.setSelectionBehavior(QAbstractItemView.SelectRows)

        #Hide Vertical Header
        #self.xmsgs.verticalHeader().setVisible(False)
        #Set Horizontal Header Properties
        #self.xmsgs.horizontalHeader().setStretchLastSection(True)
        #self.xmsgs.resizeColumnsToContents()
        #self.xmsgs.setModel(XmsgsTreeModel())

        layout = QVBoxLayout()
        layout.addWidget(self.xmsgs)
        self.setLayout(layout)
        self.path = None

    def reset(self):
        print "reset xmsgs"
        
    def set_path(self, path):
        self.path = path

    def get_finished_state(self):
        return BUILDER_RESULT.UNKNOWN

    def set_model(self, model):
        self.xmsgs.setModel(model)


class XmsgsTreeView(QTreeView):
    def __init__(self, parent, status):
        super (XmsgsTreeView, self).__init__(parent)
        self.setUniformRowHeights(True)
        #self.setModel(self.m)
        self.expand(self.rootIndex())
        self.status = status
        self.status.Debug( "Platform Tree View Started!")
        
        hdr = self.header()
        #hdr.setStretchLastSection (False)
        hdr.setDefaultSectionSize(90)

    def activated(self, index):
        #super(XmsgsTreeView, self).activated(index)
        self.status.Debug( "Activated: %d, %d" % (index.row(), index.column()))

    def clear(self):
        self.m.clear()


