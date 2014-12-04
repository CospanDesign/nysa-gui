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

import os
import sys
import xml.etree.ElementTree as ET

from PyQt4.QtCore import *
from PyQt4.QtGui import *

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             "tree_table"))

from xilinx_xmsgs_parser import XilinxXmsgsParser
from xilinx_xmsgs_parser import XilinxXmsgsParserError

from NysaGui.common.tree_table.tree_table import BranchNode
from NysaGui.common.tree_table.tree_table import TreeTableModel
from NysaGui.common.tree_table.tree_table import RootNode

builder_names = ["xst", "ngdbuild", "map", "par", "bitgen", "trce"]

class BuilderNode(BranchNode):
    def __init__(self, name, xp, tree_model, parent):
        super(BuilderNode, self).__init__(name, parent)
        self.xp = xp
        self.tree_model = tree_model
        self.messages = []
        self.filter_type = "all"
        self.delta = "false"

    def __len__(self):
        return len(self.messages)

    def childAtRow(self, row):
        assert 0 <= row < len(self.messages)
        return self.messages[row]

    def rowOfChild(self, child):
        return self.messages.indexOf(child)

    def childWithKey(self, key):
        return self.messages[key]

    def insertChild(self, child):
        assert 0

    def update(self, type_filter = [], new_items = False):
        #Update the count of messages
        self.messages += self.xp.get_messages(self.name,
                                              type_filter,
                                              new_items)
        #print "got all children: %s" % str(self.messages)

        if len(type_filter) == 0:
            self.filter_type = "all"
        else:
            self.filter_type = str(type_filter)

        #print "\tnumber of messages: %d" % len(self.messages)
        self.delta = str(new_items)
        #parent_index = self.tree_model.createIndex(self.parent.rowOfChild(self), 0, self )
        #print "\tparent index: %s" % str(parent_index)

        for m in self.messages:
            m.set("builder", self.name)

    def field(self, column):
        if column == 0:
            return self.name
        if column == 1:
            #return self.filter_type
            return self.filter_type
        if column == 2:
            return str(len(self.messages))
        #    #return self.delta
        #    #return self.delta
        #    return None
        return

    def message_field(self, row, column):
        message = self.messages[row]
        if column == 0:
            return message.get('type')
        if column == 1:
            return message.get('delta')
        if column == 2:
            data = ""
            for text in message.itertext():
                data += text
            return data
        return

class XmsgsTreeModel(TreeTableModel):

    def __init__(self, parent = None):
        super (XmsgsTreeModel, self).__init__(parent)
        self.headers = ["Tool", "Level", "Message"]
        self.xp = XilinxXmsgsParser(self.changed_cb)
        self.path = ""
        self.ready = False
        self.initialize(nesting = 1, headers = self.headers)



    def data(self, index, role):
        #Text Alignment Data
        if role == Qt.TextAlignmentRole:
            return int (Qt.AlignTop | Qt.AlignLeft)

        #Icons/Color
        if role == Qt.DecorationRole:

            node = self.nodeFromIndex(index)
            if node is None:
                return None

        #If not data to fill a box bail
        if role != Qt.DisplayRole:
            return

        node = self.nodeFromIndex(index)
        assert node is not None

        if isinstance(node, RootNode):
            print "root node!"
            return None
        if isinstance(node, BuilderNode):
            return node.field(index.column())
        if isinstance(node, ET.Element):
            name = node.get("builder")
            builder = self.root.childWithKey(name)
            return builder.message_field(index.row(), index.column())

        print "Get Data for other type"

    #Functions for use by non table interface
    def changed_cb(self, name):
        #Check if the specific builder exists in the root
        #If not add the specific builder to as a new builder node
        name = QString(name)
        print "changed_cb: %s Changed" % name
        builder = self.root.childWithKey(name)
        if builder is None:
            builder = BuilderNode(name, self.xp, self, self.root)
            print "Insert %s into root" % name
            keys = self.root.get_child_list()
            if len(keys) == 0:
                print "\tList is empty, add item to the beginning"
                self.root.insertChild(builder)

            else:
                #List is shorter than where we need to be put in
                name_index = builder_names.index(name)
                print "\tinsert %s into list: %s" % (name, keys)
                print "\tname index: %d" % name_index
                for key in keys:
                    key_index = builder_names.index(key)

                    if name_index < key_index:
                        print "%s is before %s" % (name, key)
                        self.root.insertChildAt(pos = keys.index(key), child = builder)
                        break
            #self.root.add_child(builder)

        print "\tUpdate builder"
        builder.update()
        print "reset"
        self.reset()
        #self.emit(SIGNAL("dataChanged()"))

    def status_available(self, builder):
        return builder_exists(builder)

    def pass_with_warnings(self, builder):
        try:
            if len (self.xp.get_messages(builder,
                                         type_filters = ["warning"])) > 0:
                return True
        except XilinxXmsgsParserError, err:

            #This means we don't have any messages
            return False

        return False

    def failed(self, builder):
        try:
            if len(self.xp.get_messages(builder,
                                    type_filters = ["error"])) > 0:
                return True

        except XilinxXmsgsParserError, err:
            #This means we don't have any messages
            return False

        return False

    def ready(self):
        return self.ready

    def set_path(self, path):
        self.path = path
        self.clear()
        try:
            self.xp.watch_path(path)
        except TypeError, err:
            #print "Type Error: failed to set path: %s" % str(err)
            self.ready = False
        except XilinxXmsgsParserError, err:
            #print "failed to set path"
            self.ready = False
        self.reset()


    def parent(self, index): 
        node = self.nodeFromIndex(index)
        #print "node: %s" % str(node)
        if node is None:
            return QModelIndex()

        parent = None

        if isinstance(node, ET.Element):
            parent_name = node.get("builder")
            parent = self.root.childWithKey(parent_name)
        if isinstance(node, BuilderNode):
            return QModelIndex()
        if isinstance(node, RootNode):
            return QModelIndex()

        if isinstance(node, tuple):
            return QModelIndex()

        if parent is None:
            return QModelIndex()
        grandparent = parent.parent
        if grandparent is None:
            return QModelIndex()

        row = grandparent.rowOfChild(parent)
        assert row != -1
        return self.createIndex(row, 0, parent)



