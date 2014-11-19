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

p = os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common")
p = os.path.abspath(p)
#print "Path: %s" % str(p)
sys.path.append(p)

from tree_table.tree_table import TreeTableModel
from tree_table.tree_table import BranchNode
from tree_table.tree_table import LeafNode

from designer.designer import Designer
from builder.builder import Builder
from constraints.constraints import Constraints
from configuration.configuration import Configuration

CONFIG_STATUS_DICT = {
    "ready":QColor(0xFF, 0xFF, 0xFF),
    "edit me": QColor(0xFF, 0x99, 0x00),
    "error": QColor(0xFF, 0x00, 0x00),
    "warning":QColor(0xFF, 0x99, 0x00),
    "busy":QColor(0xFF, 0x00, 0xFF)
}

def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)

CONFIG_STATE = enum ("FOCUSED", "BACKGROUND")


class ConfigNode(LeafNode):
    def __init__(self, actions, status, project, name):
        self.actions = actions
        self.status = status
        fields = ["", QString(name), ""]
        self.index = 1
        self.state = CONFIG_STATE.BACKGROUND
        self.status = "ready"
        super (ConfigNode, self).__init__(fields)
        self.w = None

    def orderKey(self):
        return self.fields[self.index].toLower()

    def field(self, column):
        """Return the field associated with the columnn"""
        if column == self.index:
            return self.fields[self.index]
        return None

    def get_name(self):
        """Return the actual name from the node"""
        return self.fields[self.index]

    def get_color(self, column):
        if column == 1:
            s = str(self.fields[self.index])
            return self.parent.project.get_view().get_color(self.fields[self.index])
        if column == 2:
            try:
                return self.parent.project.get_status()
            except:
                print "Error when getting project status!"
                pass
        return QColor(0xFF, 0xFF, 0xFF)

    def get_state(self):
        return self.state

    def set_state(self, state):
        self.state = state

    def get_status(self):
        return self.status

    def set_status(self, status):
        self.status = status

class ProjectNode(BranchNode):
    def __init__(self, parent, actions, status, project):
        super(ProjectNode, self).__init__(project.get_name(), parent)
        self.project = project
        for name in self.project.get_view_names():
            self.insertChild(ConfigNode(actions, status, project, name))

    def get_color(self, column):
        if column == 2:
            try:
                return self.project.get_status_color()
            except:
                print "Error when getting project status!"
                pass
        return None

    def get_name(self):
        return self.project.get_name()

    def get_status(self):
        return self.project.get_status()

    def get_project(self):
        return self.project

class RootBranch(BranchNode):
    def __init__(self, actions, status):
        self.actions = actions
        self.status = status
        name = "root"
        parent = None
        super (RootBranch, self).__init__(name, parent)

    def add_project(self, project):
        print "project: %s" % str(project)
        name = QString(project.get_name())
        node = ProjectNode(self, self.actions, self.status, project)
        self.insertChild(node)
        return node

    def remove_project(self, name):
        child = self.childWithKey(name)
        return self.removeChild(child)

    def get_project(self):
        return project

class ProjectTreeTableModel(QAbstractItemModel):
    def __init__(self, actions, status):
        super (ProjectTreeTableModel, self).__init__()
        self.actions = actions
        self.status = status
        self.root = RootBranch(actions, status)
        self.headers = ["Project Name", "Configuration", "Status"]
        self.nested = 1
        self.columns = len(self.headers)

        self.font = QFont("White Rabbit")
        self.font.setBold(False)

        self.focused_font = QFont("White Rabbit")
        self.focused_font.setBold(True)


    def rowCount(self, parent):
        node = self.nodeFromIndex(parent)
        if node is None:
            return 0
        if isinstance(node, ConfigNode):
            return 0
        return len(node)

    def asRecord(self, index):
        node = self.nodeFromIndex(index)
        self.status.Debug("node: %s" % QString(node))

        if node is None:
            return []
        if isinstance(node, RootBranch):
            return []
        return node.asRecord()

    def get_project_path(self, parent):
        node = self.nodeFromIndex(parent)
        if isInstance(node, ProjectNode):
            return node.get_project_path()
        if isInstance(node, ConfigNode):
            return node.parent.get_project_path()

    def remove_project(self, name, path = None):
        project = None
        #Go through the projects
        for child in self.root.children:
            if name.toLower() == child.name.toLower():
                if path is not None:
                    #Nailed it!
                    if os.path.abspath(child.get_path()) == os.path.abspath(path):
                        project = child
                        break

                #Check if we found a duplicate and the user has not specified a path
                if project is not None:
                    self.status.Error("Found a project with the same name: %s at %s and %s, please specify a path" % (name, project.get_path(), child.get_paht()))
                    return False

                project = child

        if project is None:
            self.status.Error("Cound not find project: %s" % name)
            return False

        self.status.Info("Rmove Project: %s" % name)
        self.root.removeChild(project)
        return True

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            assert 0 <= section <= len(self.headers)
            return self.headers[section]

    def columnCount(self, parent):
        return len(self.headers)

    def nodeFromIndex(self, index):
        if index.isValid():
            return index.internalPointer()
        return self.root

    def index(self, row, column, parent):
        assert self.root
        branch = self.nodeFromIndex(parent)
        assert branch is not None
        return self.createIndex(row, column, branch.childAtRow(row))

    def parent(self, child):
        node = self.nodeFromIndex(child)
        if node is None:
            return QModelIndex()
        if isinstance(node, tuple):
            return QModelIndex()
        parent = node.parent
        if parent is None:
            return QModelIndex()

        if isinstance(parent, RootBranch):
            return self.createIndex(0, 0, parent)

        if isinstance(parent, ProjectNode):
            row = self.root.rowOfChild(parent)
            return self.createIndex(row, 0, parent)

        grandparent = parent.parent
        if grandparent is None:
            return QModelIndex()

        row = grandparent.rowOfChild(parent)
        assert row != -1
        return self.createIndex(row, 0, parent)

    def clear(self):
        self.root = RootBranch(self.actions, self.status)
        self.reset()

    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            return int (Qt.AlignTop | Qt.AlignLeft)

        if role == Qt.BackgroundColorRole:
            node = self.nodeFromIndex(index)
            if isinstance(node, RootBranch):
                return

            return QBrush(node.get_color(index.column()))

        node = self.nodeFromIndex(index)
        if role == Qt.FontRole:
            if isinstance(node, ConfigNode):
                if index.column() == 1 and node.get_state() == CONFIG_STATE.FOCUSED:
                    print "Focused!"
                    return self.focused_font
            return self.font

        if role != Qt.DisplayRole:
            return

        assert node is not None
        node_value = ""

        if isinstance(node, RootBranch):
            return None
        if isinstance(node, ProjectNode):
            if index.column() == 0:
                return node.get_name()
            if index.column() == 2:
                return "%s" % node.get_status()
        if isinstance(node, ConfigNode):
            if index.column() == 1:
                return node.get_name()
            if index.column() == 2:
                return node.get_status()
        return None

    def add_project(self, project):
        return self.root.add_project(project)

    def remove_project(self, name, path = None):
        return self.root.remove_project(name, path)

class ProjectTree(QTreeView):
    def __init__(self, actions, status):
        super(ProjectTree, self).__init__()
        self.actions = actions
        self.status = status
        self.setUniformRowHeights(True)
        self.m = ProjectTreeTableModel(actions, status)
        self.setModel(self.m)
        self.expand(self.rootIndex())

        #Setup signals here
        self.status.Debug("Setting up Project Tree")
        self.setMaximumWidth(300)
        hdr = self.header()
        hdr.setDefaultSectionSize(90)

        #XXX: Connect up activated and pressed
        #XXX: Add signals to add or remove projects

        self.setSelectionModel(QItemSelectionModel(self.m))

    def contextMenuEvent(self, event):
        menu = QMenu(self.parentWidget())
        menu.addAction("New Project", self.actions.ibuilder_new_project)
        menu.exec_(self.mapToGlobal(event.pos()))

    def sizeHint (self):
        size = QSize()
        size.setWidth(300)
        return size

    def clear(self):
        self.m.clear()

    def select_first_item(self):
        self.status.Debug("Selecting First Item in ProjectTree")
        self.status.Error("Not Implemented Yet!")

    def add_project(self, project):
        return self.m.add_project(project)

    def remove_project(self, name, path = None):
        return self.m.remove_project(name, path)

    def get_project_color(self):
        pass

