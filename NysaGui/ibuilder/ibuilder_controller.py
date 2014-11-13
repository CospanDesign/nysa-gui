#! /usr/bin/python

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

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'


import sys
import os
import collections

from PyQt4.Qt import *
from PyQt4.QtCore import *


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from NysaGui.common.utils import create_hash
from ibuilder_project import IBuilderProject
from view.ibuilder_view import IBuilderView
from ibuilder_actions import Actions


class IBuilderController(QObject):
    def __init__(self, actions, status):
        super(IBuilderController, self).__init__()
        self.nysa_gui_actions = actions
        self.status = status
        self.actions = Actions()
        self.view = IBuilderView(self.actions, self.status)
        self.project_tree = self.view.get_project_tree()
        self.projects = {}

        #XXX: Demo Stuff!
        self.new_project()
        #XXX: End Demo Stuff!
        self.actions.ibuilder_new_project.connect(self.new_project)

    def new_project(self):
        self.status.Debug("New Project Clicked!")
        new_project_name_base = "project_%d"
        index = 1
        new_project_name = new_project_name_base % index
        conflict = True
        while conflict:
            conflict = False
            for project_name in self.projects:
                if project_name == new_project_name:
                    conflict = True
                    new_project_name = new_project_name_base % index
            index += 1
        #Create a populated new project
        self.add_project(new_project_name)

    def add_project(self, name, path = None):
        self.status.Debug("Add Project: %s" % name)
        ibp = IBuilderProject(self.actions, self.status, name, path)
        self.view.add_project(ibp)

    def get_view(self):
        return self.view

