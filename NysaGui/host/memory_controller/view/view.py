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

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QTextEdit
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QTabWidget
from PyQt4 import Qt

from memory_tester_widget import MemoryTesterWidget
from file_io import FileIOWidget
from memory_table import MemoryTable

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir))

class View(QWidget):

    def __init__(self, status, memory_actions):
        super (View, self).__init__()
        self.status = status
        self.memory_actions = memory_actions
        self.size = 0
        self.offset = 0

    def setup_view(self):
        self.setWindowTitle("Memory Controller")
        self.mem_label = QLabel("Memory Size/Offset:")
        layout = QVBoxLayout()
        self.mtw = MemoryTesterWidget(self.memory_actions)
        self.fio = FileIOWidget(self.status, self.memory_actions)
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.update)
        self.mem_table = MemoryTable()
        layout.addWidget(refresh_button)
        layout.addWidget(self.mem_table)
        layout.addWidget(self.mem_label)
        self.tab_view = QTabWidget()
        self.tab_view.setSizePolicy(Qt.QSizePolicy.Minimum, Qt.QSizePolicy.Minimum)
        self.tab_view.addTab(self.fio, "File IO")
        self.tab_view.addTab(self.mtw, "Tester")
        #layout.addWidget(self.fio)
        #layout.addWidget(self.mtw)
        layout.addWidget(self.tab_view)
        #layout.addWidget(btn)

        self.setLayout(layout)

    def add_test(self, name, default_enabled, func):
        self.mtw.add_row(name, default_enabled, func)

    def set_test_results(self, pos, result):
        self.mtw.test_results[pos].setText(result)

    def get_num_tests(self):
        return self.mtw.get_num_tests()

    def is_test_enabled(self, pos):
        return self.mtw.is_test_enabled(pos)

    def get_test_function(self, pos):
        return self.mtw.get_test_function(pos)

    def set_memory_size(self, size):
        self.size = size
        self.mem_label.setText("Memory Size: 0x%08X Memory Offset: 0x%08X" % (self.size, self.offset))

    def set_memory_offset(self, offset):
        self.offset = offset
        self.mem_label.setText("Memory Size: 0x%08X Memory Offset: 0x%08X" % (self.size, self.offset))

    def set_nysa(self, nysa):
        self.mem_table.set_nysa(nysa)

    def set_urn(self, urn):
        self.mem_table.set_urn(urn)

    def update(self):
        self.mem_table.invalidate()


