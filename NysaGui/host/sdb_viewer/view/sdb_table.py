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
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QFont
from PyQt4.QtGui import QColor

from color_scheme import *

p = os.path.join(os.path.dirname(__file__),
                 os.pardir,
                 os.pardir,
                 os.pardir,
                 "common",
                 "tree_table")
p = os.path.abspath(p)
#print "Path: %s" % p
sys.path.append(p)

from tree_table import TreeTableModel
from tree_table import BranchNode
from tree_table import LeafNode

KEY, NODE = range(2)

class SDBEntryNode(LeafNode):
    def __init__(self, parent, name, value, depth):
        fields = []
        super (SDBEntryNode, self).__init__(fields, parent)
        self.depth = depth
        self.name = name
        self.value = value

    def get_depth(self):
        return self.depth

    def get_name(self):
        return self.name

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

class SDBComponentBranch(BranchNode):
    def __init__(self, parent, component, depth):
        self.component = component
        name = component.get_name()
        super (SDBComponentBranch, self).__init__(name, parent)
        self.depth = depth
        self.setup_component_features()

    def setup_component_features(self):
        start_address = "0x%016X" % self.component.get_start_address_as_int()
        child = SDBEntryNode(self, "Address", start_address, self.depth)
        self.insertChild(child)

        size = "0x%016X" % self.component.get_size_as_int()
        child = SDBEntryNode(self, "Size", size, self.depth)
        self.insertChild(child)

    def orderKey(self):
        return self.name

    def get_depth(self):
        return self.depth

    def get_name(self):
        return self.name

class SDBBusBranch(BranchNode):
    def __init__(self, parent, som_component, depth):
        self.som_component = som_component
        self.component = som_component.get_component()
        name = self.component.get_name()
        self.depth = depth
        super (SDBBusBranch, self).__init__(name, parent)

    def orderKey(self):
        return self.name

    def process_bus(self):
        #print "Process: %s bus" % self.name
        #Setup the features of the bus first
        self.setup_bus_features()
        #Process all the sub comopnents
        for som_component in self.som_component:
            #print "component: %s" % som_component.get_name()
            component = som_component.get_component()
            if component.is_interconnect():
                bus = SDBBusBranch(self, som_component, self.depth + 1)
                self.insertChild(bus)
                bus.process_bus()
            else:
                component_branch = SDBComponentBranch(self, component, self.depth)
                self.insertChild(component_branch)

    def setup_bus_features(self):
        #print "setting up bus features"
        start_address = "0x%016X" % self.component.get_start_address_as_int()
        child = SDBEntryNode(self, "Address", start_address, self.depth)
        self.insertChild(child)

        size = "0x%016X" % self.component.get_size_as_int()
        child = SDBEntryNode(self, "Size", size, self.depth)
        self.insertChild(child)

        num_devices = "%d" % self.component.get_number_of_records_as_int()
        child = SDBEntryNode(self, "Count", num_devices, self.depth)
        self.insertChild(child)

    def __len__(self):
        #print "Length of children: %d" % len(self.children)
        return len(self.children)

    def get_depth(self):
        return self.depth

    def get_name(self):
        return self.name

class RootBusBranch(BranchNode):
    def __init__(self, name = ""):
        super (RootBusBranch, self).__init__(name, None)
        self.parent = None

    def __len__(self):
        return len(self.children)

    def childWithKey(self, key):
        key = key.toLower()
        if not self.children:
            return None
        i = bisect.bisect_left(self.children, (key, None))
        if self.children[i][KEY] == key:
            return self.children[i][NODE]

        if i < 0 or i >= len(self.children):
            return None

class SDBTreeModel(TreeTableModel):
    def __init__(self, parent = None):
        super (SDBTreeModel, self).__init__(parent)
        self.root = RootBusBranch("")
        self.font = QFont("White Rabbit")
        self.font.setBold(True)

    def clear(self):
        self.root = RootBusBranch("")
        self.reset()

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def rowCount (self, parent):
        node = self.nodeFromIndex(parent)
        if node is None:
            return 0
        if isinstance(node, SDBEntryNode):
            return 0

        #print "Node Type: %s, length of children: %d" % (str(node), len(node))
        return len(node)

    def set_som(self, som):
        self.som = som
        root = self.som.get_root()
        bus = SDBBusBranch(self.root, root, 0)
        bus.process_bus()
        self.root.insertChild(bus)
        self.reset()
        self.depth = self.find_som_depth()
        headers = []
        #print "depth: %s" % self.depth
        for i in range(self.depth + 1):
            if i == 0:
                headers.append("Main Bus")
            elif i < self.depth:
                headers.append("Bus/Components")
            else:
                headers.append("Info")
        self.initialize(nesting = self.depth + 1, headers = headers)

    def initialize(self, nesting, headers):
        assert nesting > 0
        self.nesting = nesting
        assert headers > 0
        self.headers = headers
        self.columns = len(self.headers)

    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignTop | Qt.AlignLeft)

        if role == Qt.FontRole:
            return self.font

        if role == Qt.BackgroundColorRole:
            node = self.nodeFromIndex(index)
            if isinstance(node, SDBBusBranch):
                if index.column() < node.get_depth():
                    return
                return QColor.fromRgb(BUS_COLOR)
            if isinstance(node, SDBComponentBranch):
                if index.column() < node.get_depth():
                    return
                c = node.component
                if c.is_integration_record():
                    return QColor.fromRgb(INTEGRATION_COLOR)
                if c.is_synthesis_record():
                    return QColor.fromRgb(SYNTHESIS_COLOR)
                if c.is_url_record():
                    return QColor.fromRgb(URL_COLOR)
                else:
                    return QColor.fromRgb(DEVICE_COLOR)
            if isinstance(node, SDBEntryNode):
                if index.column() < node.get_depth():
                    return
                return QColor.fromRgb(INFO_COLOR)

        if role != Qt.DisplayRole:
            return

        node = self.nodeFromIndex(index)
        assert node is not None

        if isinstance(node, RootBusBranch):
            return None
        if isinstance(node, SDBBusBranch):
            depth = node.get_depth()
            if index.column() == depth:
                return "Bus: %s" % node.get_name()
        if isinstance(node, SDBComponentBranch):
            depth = node.get_depth()
            if index.column() == depth:
                c = node.component
                if c.is_integration_record():
                    return "Integration: %s" % node.get_name()
                if c.is_synthesis_record():
                    return "Synthesis"
                if c.is_url_record():
                    return "URL"
                else:
                    return "Device: %s" % node.get_name()
        if isinstance(node, SDBEntryNode):
            depth = node.get_depth()
            if index.column() == depth:
                return node.get_name()
            if index.column() == depth + 1:
                return node.get_value()
        return None

    def find_som_depth(self):
        depth = 1
        final_depth = 0
        root = self.som.get_root()
        for component in root:
            c = component.get_component()
            if c.is_interconnect():
                temp_depth = self._find_som_depth(component, depth + 1)
                if temp_depth > final_depth:
                    final_depth = temp_depth

        return final_depth

    def _find_som_depth(self, bus, depth):
        final_depth = depth
        for component in bus:
            c = component.get_component()
            if c.is_interconnect():
                temp_depth = self._find_som_depth(component, depth + 1)
                if temp_depth > final_depth:
                    final_depth = temp_depth
        return final_depth

class SDBTree(QTreeView):

    def __init__(self, parent = None):
        super (SDBTree, self).__init__(parent)
        self.som = None
        self.setUniformRowHeights(True)
        self.m = SDBTreeModel(parent)
        self.setModel(self.m)
        self.expand(self.rootIndex())
        self.setMaximumWidth(1000)

    def sizeHint(self):
        size = QSize()
        size.setWidth(1000)
        return size

    def set_som(self, som):
        self.m.set_som(som)

    def clear(self):
        self.m.clear()

    def resize_columns(self):
        count = self.m.columnCount(None)
        for i in range(count):
            self.resizeColumnToContents(i)

    def expandAll(self):
        super(SDBTree, self).expandAll()
        self.resize_columns()

