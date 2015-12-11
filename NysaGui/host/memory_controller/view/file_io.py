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


""" nysa interface
"""

__author__ = 'email@example.com (name)'

import sys
import os
from array import array as Array

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QCheckBox
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QHBoxLayout

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))

from save_loader import SaveLoader

class FileIOWidget(QWidget):

    def __init__(self, status, actions):
        super (FileIOWidget, self).__init__()
        self.loader = SaveLoader(load_only = True)
        self.loader.set_load_callback(self.load_callback)
        self.saver = SaveLoader(save_only = True)
        self.saver.set_save_callback(self.save_callback)

        self.s = status
        self.a = actions
        self.file_reader = None
        self.file_writer = None

        self.f2m_button = QPushButton("File to Mem")
        self.f2m_button.clicked.connect(self.f2m_button_clicked)
        self.f2m_button.setEnabled(False)
        self.m2f_button = QPushButton("Mem to File")
        self.m2f_button.clicked.connect(self.m2f_button_clicked)
        self.m2f_button.setEnabled(False)
        
        wal = QHBoxLayout()
        self.write_address = QLineEdit("0x00")
        wal.addWidget(QLabel("Addr:"))
        wal.addWidget(self.write_address)

        ral = QHBoxLayout()
        self.read_address = QLineEdit("0x00")
        ral.addWidget(QLabel("Addr:"))
        ral.addWidget(self.read_address)

        wcl = QHBoxLayout()
        self.write_data_count = QLineEdit("0x00")
        wcl.addWidget(QLabel("Count:"))
        wcl.addWidget(self.write_data_count)

        rcl = QHBoxLayout()
        self.read_data_count = QLineEdit("0x100")
        rcl.addWidget(QLabel("Count:"))
        rcl.addWidget(self.read_data_count)

        self.helper_w2r_addr_btn = QPushButton(">")
        self.helper_w2r_addr_btn.clicked.connect(self.update_read_addr)
        self.helper_w2r_count_btn = QPushButton(">")
        self.helper_w2r_count_btn.clicked.connect(self.update_read_count)

        self.lyt = QGridLayout()

        self.lyt.addWidget(QLabel("To Memory"), 0, 0)
        self.lyt.addWidget(self.loader, 1, 0)
        #self.lyt.addWidget(QLabel(""), 1, 0)
        self.lyt.addLayout(wal, 2, 0)
        self.lyt.addLayout(wcl, 3, 0)
        self.lyt.addWidget(self.f2m_button, 4, 0)

        self.lyt.addWidget(QLabel("Helper"), 0, 1)
        #self.lyt.addWidget(QLabel(""), 1, 1)
        self.lyt.addWidget(self.helper_w2r_addr_btn, 2, 1)
        self.lyt.addWidget(self.helper_w2r_count_btn, 3, 1)

        self.lyt.addWidget(QLabel("From Memory"), 0, 2)
        self.lyt.addWidget(self.saver, 1, 2)
        #self.lyt.addWidget(QLabel(""), 1, 2)
        self.lyt.addLayout(ral, 2, 2)
        self.lyt.addLayout(rcl, 3, 2)
        self.lyt.addWidget(self.m2f_button, 4, 2)

        self.setLayout(self.lyt)

    def update_read_addr(self):
        self.read_address.setText(self.write_address.text())

    def update_read_count(self):
        self.read_data_count.setText(self.write_data_count.text())

    def m2f_button_clicked(self):
        filename = self.saver.get_filename()
        print "M2F Filename: %s" % filename
        address = int(str(self.read_address.text()), 0)
        count = int(str(self.read_data_count.text()), 0)
        self.a.memory_memory_2_file.emit(filename, address, count)

    def f2m_button_clicked(self):
        filename = self.loader.get_filename()
        print "F2M Filename: %s" % filename
        address = int(str(self.write_address.text()), 0)
        count = int(str(self.write_data_count.text()), 0)
        self.a.memory_file_2_memory.emit(filename, address, count)

    def load_callback(self):
        filename = self.loader.get_filename()
        self.read_data_count.setText("0x00")
        if not os.path.exists(filename):
            self.f2m_button.setEnabled(False)
            return
        self.f2m_button.setEnabled(True)
        f = open(filename, "rb")
        d = Array('B')
        d.fromstring(f.read())
        f.close()
        self.write_data_count.setText(hex(len(d)))

    def save_callback(self):
        filename = self.saver.get_filename()
        if not os.path.exists(filename):
            self.m2f_button.setEnabled(False)
            return
        self.m2f_button.setEnabled(True)

