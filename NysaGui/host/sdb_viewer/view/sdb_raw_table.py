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

from PyQt4.QtGui import QTreeView
from PyQt4.Qt import QSize
from PyQt4.Qt import QString
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QFont
from PyQt4.QtGui import QColor

from color_scheme import *


p = os.path.join(os.path.dirname(__file__),
                 os.pardir,
                 os.pardir,
                 os.pardir,
                 os.pardir)


p = os.path.abspath(p)
#print "Path: %s" % p
sys.path.append(p)

from NysaGui.common.tree_table.tree_table import TreeTableModel
from NysaGui.common.tree_table.tree_table import BranchNode
from NysaGui.common.tree_table.tree_table import LeafNode

KEY, NODE = range(2)

class SDBRawNode(LeafNode):
    def __init__(self, parent, value):
        fields = [value]
        super (SDBRawNode, self).__init__(fields, parent)

    def field(self, column):
        if column == 1:
            return self.fields[0]

class SDBComponentBranch(BranchNode):
    def __init__(self, parent, index, name):
        super (SDBComponentBranch, self).__init__(name, parent)
        self.fields = [index, name]
        self.name = name

    def __len__(self):
        return len(self.children)

    def is_first_index(self):
        index = int(self.fields[0], 16)
        if index % 8 == 0:
            return True
        return False

    def field(self, column):
        assert 0 <= column <= len(self.fields)
        return self.fields[column]

class SDBRawRoot(BranchNode):
    def __init__(self, name, parent=None):
        super (SDBRawRoot, self).__init__("", parent)
        self.parent = None

    def __len__(self):
        return len(self.children)

    def childWithKey(self, key):
        key = QString(key).toLower()
        if not self.children:
            return None
        i = bisect.bisect_left(self.children, (key, None))
        if self.children[i][KEY] == key:
            return self.children[i][NODE]

        if i < 0 or i >= len(self.children):
            return None

    def remove_type(self, type_name):
        c = None
        for child in self.children:
            if QString(child[NODE].name).toLower() == str(type_name).toLower():
                c = child
                break
        self.children.remove(c)

    def insertChild(self, child):
        child.parent = self
        self.children.append(child)

    def removeChild(self, child):
        self.children.remove(child)

class SDBRawTreeModel(TreeTableModel):

    def __init__(self, parent = None):
        self.root = SDBRawRoot("")
        super (SDBRawTreeModel, self).__init__(parent)
        headers = ["Address", "Type/ROM Block"]
        self.initialize(nesting = 1, headers = headers)
        self.font = QFont("White Rabbit")
        self.font.setBold(True)

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def rowCount (self, parent):
        node = self.nodeFromIndex(parent)
        if node is None:
            return 0
        if isinstance(node, SDBComponentBranch):
            return len(node)
        if isinstance(node, SDBRawNode):
            return 0
        return len(node)

    def asRecord(self, index):
        node = self.nodeFromIndex(index)

        #Only return valid records
        if node is None:
            return []
        if isinstance(node, SDBRawRoot):
            return []
        if isinstance(node, SDBComponentBranch):
            return [node.asRecord()]
        if isinstance(node, SDBRawNode):
            return node.asRecord()

    def addRecord(self, index, address, name, raw_list):
        root = self.root

        #There is no branch with that name
        component_branch = root.childWithKey(index)

        if component_branch is None:
            #This thing doesn't exist
            #all type branches are children of root
            component_branch = SDBComponentBranch(root, address, name)
            root.insertChild(component_branch)

        for raw in raw_list:
            raw_node = SDBRawNode(component_branch, raw)
            component_branch.insertChild(raw_node)

        #This may not be needed
        self.reset()

    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignTop | Qt.AlignLeft)

        if role == Qt.FontRole:
            return self.font

        if role == Qt.BackgroundColorRole:
            if index.column() == 0:
                if index.row() != 0:
                    node = self.nodeFromIndex(index)

            if index.column() == 2:
                if index.row() != 0:
                    node = self.nodeFromIndex(index)

            if index.column() == 1:
                node = self.nodeFromIndex(index)

                if isinstance(node, SDBRawNode):
                    node = node.parent

                if isinstance(node, SDBComponentBranch):
                    if node.name == "Interconnect":
                        return QColor.fromRgb(BUS_COLOR)
                    if node.name == "Bridge":
                        return QColor.fromRgb(BRIDGE_COLOR)
                    if node.name == "Empty":
                        return QColor.fromRgb(EMPTY_COLOR)
                    if node.name == "Device":
                        return QColor.fromRgb(DEVICE_COLOR)
                    if node.name == "URL":
                        return QColor.fromRgb(URL_COLOR)
                    if node.name == "Synthesis":
                        return QColor.fromRgb(SYNTHESIS_COLOR)
                    if node.name == "Integration":
                        return QColor.fromRgb(INTEGRATION_COLOR)
                    if node.name == "???":
                        return QColor.fromRgb(UNKOWN_COLOR)
                    return QColor.fromRgb(BAD_CHOICE_COLOR)


        if role != Qt.DisplayRole:
            return

        node = self.nodeFromIndex(index)
        assert node is not None

        node_value = ""
        if isinstance(node, SDBRawRoot):
            return None
        if isinstance(node, SDBComponentBranch):
            return node.field(index.column())
        if isinstance(node, SDBRawNode):
            return node.field(index.column())
        return None

class SDBRawTree(QTreeView):

    def __init__(self, parent = None):
        super (SDBRawTree, self).__init__(parent)
        self.setUniformRowHeights(True)
        self.m = SDBRawTreeModel(parent)
        self.setModel(self.m)
        self.expand(self.rootIndex())
        self.setMaximumWidth(1000)

    def sizeHint(self):
        size = QSize()
        size.setWidth(1000)
        return size

    def add_entry(self, index, address, name, raw):
        self.m.addRecord(index, address, QString(name), raw)

    def clear(self):
        self.m.clear()

    def resize_columns(self):
        count = self.m.columnCount(None)
        for i in range(count):
            self.resizeColumnToContents(i)

        self.expandAll()


