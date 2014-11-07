#!/usr/bin/env python
# Copyright (c) 2007-8 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.


"""
This code was mostly taken from the Rapid Gui Development with Python and Qt

as such this file uses the GNU copyright

by: Mark Summerfield

"""

import sys
import os
import hashlib

import bisect
from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *


KEY, NODE = range(2)

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir))


sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from actions import Actions


from tree_table import TreeTableModel
from tree_table import BranchNode
from tree_table import LeafNode


class DeviceNode(LeafNode):
    def __init__(self, name, data):
        self.name = name
        self.data = data
        super (DeviceNode, self).__init__(["", "", name])

    def get_name(self):
        return self.name

    def get_id(self):
        return self.name

    def orderKey(self):
        return self.name.toLower()

    def get_data(self):
        return self.data

    def get_color(self):
        return QColor(Qt.blue)

class SubTypeBranch(BranchNode):
    def __init__(self, name):
        super (SubTypeBranch, self).__init__(name)

    def __len__(self):
        return len(self.children)

    def remove_device(self, entity_name):
        c = None
        node = None
        for child in self.children:
            if child[NODE].get_id() == entity_name:
                c = child
                node = c[NODE]

        if node is None:
            return False

        self.children.remove(c)
        return True

    def get_child_with_type(self, name):
        for child in self.children:
            if child.get_name() == name:
                return child
        return None

    def get_name(self):
        return self.name

class TypeBranch(BranchNode):
    def __init__(self, name):
        super (TypeBranch, self).__init__(name)

    def __len__(self):
        return len(self.children)

    def get_child_with_type(self, name):
        for child in self.children:
            if child.get_name() == name:
                return child
        return None

    def get_name(self):
        return self.name

class RootBranch(BranchNode):
    def __init__(self, name):
        super (RootBranch, self).__init__("")
        self.parent = None

    def __len__(self):
        return len(self.children)

    def get_child_with_type(self, name):
        for child in self.children:
            if child.get_name() == name:
                return child
        return None

    def removeChild(self, child):
        self.children.remove(child)

class PlatformTreeTableModel(QAbstractItemModel):
    def __init__(self, parent = None):
        super (PlatformTreeTableModel, self).__init__(parent)
        self.root = RootBranch("")
        self.headers = ["Type", "Sub Type", "Name"]
        self.nested = 2
        self.columns = len(self.headers)

        self.font = QFont("White Rabbit")
        self.font.setBold(True)

    def flags (self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def rowCount (self, parent):
        node = self.nodeFromIndex(parent)
        if node is None:
            return 0
        if isinstance(node, DeviceNode):
            return 0
        return len(node)

    def asRecord(self, index):
        node = self.nodeFromIndex(index)
        print (str(node))

        #Only return valid records
        if node is None:
            return []
        if isinstance(node, RootBranch):
            return []
        if isinstance(node, TypeBranch):
            return []
        if isinstance(node, SubTypeBranch):
            return []
        if isinstance(node, DeviceNode):
            return node.asRecord()

    def get_nysa_device(self, index):
        node = self.nodeFromIndex(index)
        if isinstance(node, DeviceNode):
            return node.get_data()
        return None

    def get_entity_type(self, index):
        node = self.nodeFromIndex(index)
        if isinstance(node, DeviceNode):
            return node.parent.get_name()
        return None

    def addRecord(self, type_name, sub_type_name, entity_name, data):
        root = self.root

        #Get a reference to the type branch
        type_branch = root.get_child_with_type(type_name)

        if type_branch is None:
            #This thing doesn't exist
            type_branch = TypeBranch(type_name)
            root.insertChild(type_branch)

        #Get an instance of the sub type with the name
        sub_type_branch = type_branch.get_child_with_type(sub_type_name)
        
        if sub_type_branch is None:
            sub_type_branch = SubTypeBranch(sub_type_name)
            type_branch.insertChild(sub_type_branch)

        #Get a reference to the device type
        device_node = sub_type_branch.get_child_with_type(entity_name)

        if device_node is None:
            print "Insert Device"
            device_node = DeviceNode(entity_name, data)
            sub_type_branch.insertChild(device_node)

        print "Children of sub types"
        for c in sub_type_branch.children:
            print "Child: %s" % str(c)

        #This may not be needed
        self.reset()

    def removeRecord(self, entity_name):
        root = self.root
        dev_node = None
        type_branch = None
        sub_type_branch = None
        for branch_index in range (len(root)):
            branch = root.childAtRow(branch_index)
            for sub_type_index in range(len(branch)):
                sub_type_name = branch.childAtRow(sub_type_index)
                for dev_index in range(len(sub_type_name)):
                    child = sub_type_name.childAtRow(dev_index)
                    if child.get_id() == entity_name:
                        dev_node = child
                        break
                
            if dev_node is not None:
                type_branch = branch
                sub_type_branch = sub_type_name
                break

        if dev_node is not None:
            type_branch.removeChild(dev_node)
            dev_node = None

        if len(sub_type_branch) == 0:
            type_branch.removeChild(sub_type_branch)

        if len(type_branch) == 0:
            root.removeChild(type_branch)
            type_branch = None

        #This may not be needed
        self.reet()

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            assert 0 <= section <= len(self.headers)
            return self.headers[section]

    def columnCount(self, parent):
        return len(self.headers)

    def nodeFromIndex(self, index):
        if index.isValid():
            node = index.internalPointer()
            print "valid: %s" % node.name
            return index.internalPointer()
        return self.root

    def index(self, row, column, parent):
        assert self.root
        branch = self.nodeFromIndex(parent)
        assert branch is not None
        #print "Branch at %d: %d: %s" % (row, column, str(branch))
        return self.createIndex(row, column, branch.childAtRow(row))
        
    def parent(self, child):
        print "Get Parent"
        node = self.nodeFromIndex(child)
        if node is None:
            return QModelIndex()
        if isinstance(node, tuple):
            print "Tuple: %s" % str(node)
            return QModelIndex()
        parent = node.parent
        if parent is None:
            print "Parent of %s is None" % str(node)
            return QModelIndex()


        if isinstance (parent, RootBranch):
            print "\tParent = Root"
            return self.createIndex(0, 0, parent)

        if isinstance (parent, TypeBranch):
            print "\tParent = Type Branch"
            row = self.root.rowOfChild(parent)
            return self.createIndex(row, 0, parent)

        grandparent = parent.parent
        if grandparent is None:
            return QModelIndex()
        row = grandparent.rowOfChild(parent)
        assert row != -1
        print "\t??"

        return self.createIndex(row, 0, parent)

    def clear (self):
        self.root = RootBranch("")
        self.reset()

    def is_nysa_device(self, index):
        node = self.nodeFromIndex(index)
        if isinstance(node, DeviceNode):
            return True
        return False

    def first_device_index(self):
        for r in range(len(self.root)):
            type_branch = self.root.childAtRow(r)
            for cr in range(len(type_branch)):
                for tr in range (len(cr)):

                    dev_node = type_branch.childAtRow(tr)
                    if dev_node is None: 
                        continue
                    grandparent = self.root
                    roc = grandparent.rowOfChild(type_branch)
                    print "Found Row of child: %d" % roc
                    print "Type: %s" % dev_node.parent.get_name()
                    return self.createIndex(roc, 0, dev_node)

        return None

    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignTop | Qt.AlignLeft)
        '''
        if role == Qt.DecorationRole:
            node = self.nodeFromIndex(index)
            if isinstance(node, TypeBranch)
                if index.column() == 0:
                    return node.get_pixmap()
        '''
        if role == Qt.BackgroundColorRole:
            node = self.nodeFromIndex(index)
            if not isinstance(node, DeviceNode):
                return

            if index.column() == 2:
                return QBrush(node.get_color())

        if role != Qt.DisplayRole:
            return

        node = self.nodeFromIndex(index)
        assert node is not None
        print "Index: %d, %d: %s" % (index.row(), index.column(), str(node))

        node_value = ""
        if isinstance(node, RootBranch):
            return None
        if isinstance(node, TypeBranch):
            if index.column() == 0:
                return node.toString()
            return None
        if isinstance(node, SubTypeBranch):
            if index.column() == 1:
                return node.toString()
            return None

        if isinstance(node, DeviceNode):
            print "node.name: %s" % node.get_name()
            if index.column() == 2:
                return node.get_name()
            return None

        return None

class PlatformTree(QTreeView):
    def __init__(self, actions, parent = None):
        super (PlatformTree, self).__init__(parent)
        self.setUniformRowHeights(True)
        self.m = PlatformTreeTableModel()
        self.setModel(self.m)
        self.expand(self.rootIndex())
        self.actions = actions
        #self.actions.add_device_signal.connect(self.add_device)

        self.actions.clear_platform_tree_signal.connect(self.clear)

        self.actions.add_verilog_core.connect(self.add_verilog_core)
        self.actions.add_image_config.connect(self.add_image_config)

        self.actions.platform_tree_get_first_dev.connect(self.select_first_item)
        print ( "Platform Tree View Started!")
        self.setMaximumWidth(300)
        
        hdr = self.header()
        #hdr.setStretchLastSection (False)
        hdr.setDefaultSectionSize(90)
        self.connect(self, SIGNAL("activated(QModelIndex)"), self.activated)
        self.connect(self, SIGNAL("pressed(QModelIndex)"), self.item_pressed)
        #self.connect(self, SIGNAL("SelectionChanged(QModelIndex)"), self.item_pressed)
        self.sm = QItemSelectionModel(self.m)
        self.setSelectionModel(self.sm)

    def sizeHint (self):
        size = QSize()
        size.setWidth(300)
        return size

    def add_verilog_core(self, core_type, data):
        print "Add Verilog Core"
        self.m.addRecord(QString("Core"), QString("Slave"), QString("DRT"), data)

    def add_image_config(self, config_dict):
        print "Add Image Clicked"
        self.m.addRecord(QString("Image"), QString("Dionysus"), QString("Bill"), config_dict)

    def add_device(self, type_name, sub_type_name, entity_name, data):
        self.m.addRecord(type_name, sub_type_name, entity_name, data)
        self.expandAll()

    def remove_device(self, entity_name):
        self.m.removeRecord(entity_name)

    def get_node_color(self, index):
        node = self.m.nodeFromIndex(index)
        if isinstance(node, DeviceNode):
            return node.get_color()
        return None

    def get_entity_name(self, index):
        l = self.m.asRecord(index)

    def activated(self, index):
        print ("Activated")
        #super(PlatformTree, self).activated(index)

    def clear(self):
        self.m.clear()

    def select_first_item(self):
        print ( "Selecting first device in platform tree")
        index = self.m.first_device_index()
        if index is not None:
            nysa_dev = self.m.get_nysa_device(index)
            nysa_type = self.m.get_entity_type(index)
            uid = self.m.nodeFromIndex(index).get_id()
            #print "Type: %s" % nysa_type
            #print "Device: %s" % str(type(nysa_dev))
            #print "ID: %s" % uid
            self.sm.select(index, QItemSelectionModel.Rows | QItemSelectionModel.Select)
            self.actions.platform_tree_changed_signal.emit(uid, nysa_type, nysa_dev)

    def item_pressed(self, index):
        print ("Item Pressed")
        if not self.m.is_nysa_device(index):
            return

        nysa_dev = self.m.get_nysa_device(index)
        nysa_type = self.m.get_entity_type(index)
        uid = self.m.nodeFromIndex(index).get_id()
        self.actions.platform_tree_changed_signal.emit(uid, nysa_type, nysa_dev)

