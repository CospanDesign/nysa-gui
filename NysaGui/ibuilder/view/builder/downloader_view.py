# -*- coding: utf-8 *-*

# Distributed under the MIT licesnse.
# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

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

'''
Log
  07/20/2013: Initial commit
'''

import os
import sys
import json

from PyQt4.QtCore import *
from PyQt4.QtGui import *

sys.path.append(os.path.join( os.path.dirname(__file__),
                                os.pardir,
                                os.pardir,
                                "gui_utils"))
class DownloaderView(QWidget):

    def __init__(self, actions, status):
        super (DownloaderView, self).__init__()
        self.actions = actions
        self.status = status

        self.setWindowTitle("Downloader")
        self.downloader_workdir = os.curdir
        self.downloader_script = None
        self.downloader_flags = []
        layout = QGridLayout()

        #Add the Build Image combobox
        self.image_select_cb = QComboBox()
        self.image_select_cb.addItem("Use Current Build Item")
        self.image_select_cb.addItem("Select Image File")
        self.image_select_cb.setCurrentIndex(0)

        #Add file selector
        self.image_dir = QLineEdit()

        #Add download button
        program_button = QPushButton("Program")
        program_button.clicked.connect(self.program)
        
        #Add all item to the combobox
        layout.addWidget(QLabel("Image:"), 0, 0, 1, 1)
        layout.addWidget(self.image_dir, 0, 1, 1, 1)
        layout.addWidget(program_button, 1, 0, 2, 2)
        self.setLayout(layout)
        self.set_background_color(0, 200, 100)

    def set_downloader_script(self, workdir, script, flags = []):
        self.downloader_workdir = workdir
        self.downloader_script = script
        self.downloader_flags = flags

    def program(self):
        self.status.Error("Program is not implemented yet!")
        if self.downloader_script is None:
            print "Downloader script is None, can't program"
            command = "echo"
            flags = ["downloader script not set"]

            #self.console.run_command(os.curdir, command, flags)
            return

    def set_background_color(self, r, g, b):
        self.setAutoFillBackground(True)
        color = QColor(r, g, b)
        p = self.palette()
        p.setColor(self.backgroundRole(), color)
        self.setPalette(p)

