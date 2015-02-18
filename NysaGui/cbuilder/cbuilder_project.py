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
import copy
import json

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

#from view.project_view import ProjectView

from nysa.ibuilder.lib import utils
from nysa.ibuilder.lib import verilog_utils as vutils

PROJECT_STATUS_DICT = {
    "unsaved":QColor(0xFF, 0x99, 0x00),
    "ready":QColor(0xFF, 0xFF, 0xFF),
    "saved":QColor(0x00, 0xFF, 0x00),
    "error":QColor(0xFF, 0x00, 0x00),
    "busy":QColor(0xFF, 0x00, 0xFF)
}


class CBuilderProject(QObject):

    def __init__(self, actions, status, name, path = None):
        super(CBuilderProject, self).__init__()
        self.actions = actions
        self.status = status
        #self.project_actions = CBuilderProjectActions()
        self.project_view = None
        self.name = name
        self.status.Info("Adding project: %s" % name)
        self.project_status = "saved"

    def update_project(self):
        #self.project_view.update_view()
        print "update project"

    def load_project(self):
        #self.config_dict = json.load(open(str(self.path), 'r'))
        print "load project"

    def get_name(self):
        return QString(self.name)

    def set_name(self, name):
        self.name = name

    def get_path(self):
        return self.path

    def set_path(self, path):
        self.path = path

    def new_change(self):
        self.project_status = "unsaved"

    def save_project(self):
        self.project_status = "saved"

    def get_status(self):
        return self.project_status

    def get_status_color(self):
        return PROJECT_STATUS_DICT[self.project_status]

    def get_view(self):
        return self.project_view

    def get_view_names(self):
        return []
