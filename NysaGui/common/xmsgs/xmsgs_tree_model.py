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

from functools import partial

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             "tree_table"))

from xilinx_xmsgs_parser import XilinxXmsgsParser
from xilinx_xmsgs_parser import XilinxXmsgsParserError

from NysaGui.common.tree_table.tree_table import RootNode
from NysaGui.common.tree_table.tree_table import BranchNode
from NysaGui.common.tree_table.tree_table import LeafNode
from NysaGui.common.tree_table.tree_table import TreeTableModel

builder_names = ["xst", "ngdbuild", "map", "par", "bitgen", "trce"]

TIMEOUT_MS = 1000

class ElementNode(LeafNode):
    def __init__(self, message, parent):
        fields = []
        self.message = message
        fields.append(self.message.get("builder"))
        fields.append(self.message.get("type"))
        #fields.append(self.message.get("delta"))
        data = ""
        for text in message.itertext():
            data += text
        fields.append(data)
        super (ElementNode, self).__init__(fields, parent)

    def orderKey(self):
        return self.message.get("builder").toLower()

    def get_color(self):
        if self.message.get("type") == "info":
            return QColor("white")
        if self.message.get("type") == "warning":
            return QColor("yellow")
        if self.message.get("type") == "error":
            return QColor("red")

class BuilderNode(BranchNode):
    def __init__(self, name, xp, tree_model, parent):
        super(BuilderNode, self).__init__(name, parent)
        self.xp = xp
        self.m = tree_model
        self.filter_type = "all"
        self.delta = "false"

    def update(self, type_filter = [], new_items = False):
        #Update the count of messages
        messages = self.xp.get_messages(self.name,
                                        type_filter,
                                        new_items)
        #print "timestamp: %s" % self.xp.message_timestamp()
        #print "got all children: %s" % str(self.messages)

        if len(type_filter) == 0:
            self.filter_type = "all"
        else:
            self.filter_type = str(type_filter)

        self.delta = str(new_items)
        message_count = len(messages)
        if message_count == 0:
            self.children = []

        if message_count > len(self.children):
            index = self.m.createIndex(self.parent.rowOfChild(self), 0)
            self.m.beginInsertRows(index, message_count, len(self.children))
            for i in range(len(self.children), message_count):
                m = messages[i]
                m.set("builder", self.name)
                e = ElementNode(m, self)
                self.insertChild(e)
            self.m.endInsertRows()

    def field(self, column):
        if column == 0:
            return self.name
        if column == 1:
            #return self.filter_type
            return self.filter_type
        if column == 2:
            return str(len(self.children))
        return

class XmsgsTreeModel(TreeTableModel):

    def __init__(self, parent = None):
        super (XmsgsTreeModel, self).__init__(parent)
        self.headers = ["Tool", "Level", "Message"]
        self.xp = XilinxXmsgsParser(self.changed_cb)
        self.xmsgs_thread = QThread()
        self.xp.moveToThread(self.xmsgs_thread)
        self.path = ""
        self.ready = False
        self.initialize(nesting = 1, headers = self.headers)
        self.update_dict = {}

    def data(self, index, role):
        #Text Alignment Data
        if role == Qt.TextAlignmentRole:
            return int (Qt.AlignTop | Qt.AlignLeft)

        #Icons/Color
        if role == Qt.DecorationRole:

            node = self.nodeFromIndex(index)
            if node is None:
                return None

        if role == Qt.BackgroundRole:
            node = self.nodeFromIndex(index)
            if node is None:
                return None
            if isinstance(node, ElementNode):
                if index.column() == 1:
                    return QBrush(node.get_color())


        #If not data to fill a box bail
        if role != Qt.DisplayRole:
            return

        node = self.nodeFromIndex(index)
        assert node is not None

        if isinstance(node, RootNode):
            #print "root node!"
            return None
        if isinstance(node, BuilderNode):
            return node.field(index.column())
        if isinstance(node, ElementNode):
            #builder = node.parent()
            return node.field(index.column())
            #return builder.message_field(index.row(), index.column())

        print "Get Data for other type"

    #Functions for use by non table interface
    def changed_cb(self, name):
        #Check if the specific builder exists in the root
        #If not add the specific builder to as a new builder node
        '''
        if name not in self.update_dict:
            print "Adding %s" % name
            self.update_dict[name] = QTimer(self)
            self.update_dict[name].setSingleShot(True)
            self.update_dict[name].setInterval(TIMEOUT_MS)
            self.update_dict[name].timeout.connect(partial(self.process_change, name))
            self.update_dict[name].start()
            self.process_change(name)
            return

        if not self.update_dict[name].isActive():
            print "timer finished for %s..." % name
            self.update_dict[name].start()
            self.process_change(name)
            return

        print "ignore"
        '''
        self.process_change(name)

    def manual_directory_update(self):
        self.xp.parse_files_in_directory()

    def process_change(self, name):
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
                insert_at_end = True
                for key in keys:
                    key_index = builder_names.index(key)

                    if name_index < key_index:
                        print "%s is before %s" % (name, key)
                        self.root.insertChildAt(pos = keys.index(key), child = builder)
                        insert_at_end = False
                        break

                
                if insert_at_end:
                    self.root.insertChild(builder)
                        #break

            #self.root.add_child(builder)

        print "\tUpdate builder"
        builder.update()
        print "reset"
        self.reset()
        #index = self.createIndex(self.root.rowOfChild(builder), 0)
        #self.reset()
        #self.fetchMore(index)
        
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
        if not os.path.exists(path):
            os.makedirs(path)
        try:
            #self.xp.watch_path(path)
            self.xp.path = path
            self.xp.parse_files_in_directory()
            pass
        except TypeError, err:
            #print "Type Error: failed to set path: %s" % str(err)
            self.ready = False
        except XilinxXmsgsParserError, err:
            #print "failed to set path"
            self.ready = False
        self.reset()


