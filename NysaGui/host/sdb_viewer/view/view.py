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


""" SDB Viewer... view
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QToolBar
from PyQt4.QtGui import QPushButton
from PyQt4.QtCore import Qt

from .sdb_table import SDBTree
from .sdb_raw_table import SDBRawTree

class View(QWidget):

    def __init__(self, status = None, Actions = None):
        super (View, self).__init__()

        self.setWindowTitle("Standalone View")
        self.sdb_tree_table = SDBTree(self)
        self.sdb_raw_tree_table = SDBRawTree(self)
        main_layout = QVBoxLayout()

        #Create the buttons
        expand_raw_button = QPushButton("Expand All")
        collapse_raw_button = QPushButton("Collapse All")

        expand_parsed_button = QPushButton("Expand All")
        collapse_parsed_button = QPushButton("Collapse All")

        #Connect the signals
        expand_raw_button.clicked.connect(self.sdb_raw_tree_table.expandAll)
        collapse_raw_button.clicked.connect(self.sdb_raw_tree_table.collapseAll)

        expand_parsed_button.clicked.connect(self.sdb_tree_table.expandAll)
        collapse_parsed_button.clicked.connect(self.sdb_tree_table.collapseAll)



        layout = QHBoxLayout()
        main_layout.addLayout(layout)

        raw_tree_table_layout = QVBoxLayout()
        raw_tree_table_layout.addWidget(QLabel("Raw SDB"))
        l = QHBoxLayout()
        l.addWidget(expand_raw_button)
        l.addWidget(collapse_raw_button)
        raw_tree_table_layout.addLayout(l)
        raw_tree_table_layout.addWidget(self.sdb_raw_tree_table)

        parsed_tree_table_layout = QVBoxLayout()
        parsed_tree_table_layout.addWidget(QLabel("Parsed SDB"))
        l = QHBoxLayout()
        l.addWidget(expand_parsed_button)
        l.addWidget(collapse_parsed_button)
        parsed_tree_table_layout.addLayout(l)
        parsed_tree_table_layout.addWidget(self.sdb_tree_table)

        layout.addLayout(raw_tree_table_layout)
        layout.addLayout(parsed_tree_table_layout)
        self.text = ""
        self.te = QLabel(self.text)
        self.te.setMaximumWidth(500)
        self.te.setWordWrap(True)
        self.te.setAlignment(Qt.AlignTop)
        layout.addWidget(self.te)

        #self.setLayout(layout)
        self.setLayout(main_layout)
        self.text = ""
        self.te.setText("")

    def append_text(self, text):
        self.text += text
        self.te.setText(self.text)

    def clear_text(self):
        self.text = ""
        self.te.setText("")

    #SDB Parsed Table
    def set_sdb_parsed_som(self, som):
        self.sdb_tree_table.set_som(som)

    def clear_table(self):
        self.sdb_tree_table.clear()

    def resize_columns(self):
        self.sdb_tree_table.resize_columns()
        self.sdb_raw_tree_table.resize_columns()

    #SDB Raw
    def add_sdb_raw_entry(self, index, address, name, raw):
        self.sdb_raw_tree_table.add_entry(index, address, name, raw)

    def clear_sdb_raw_table(self):
        self.sdb_raw_table.clear()


