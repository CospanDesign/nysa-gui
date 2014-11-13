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

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from view.project_view import ProjectView
PROJECT_STATUS_DICT = {
    "unsaved":QColor(0xFF, 0x99, 0x00),
    "ready":QColor(0xFF, 0xFF, 0xFF),
    "saved":QColor(0x00, 0xFF, 0x00),
    "error":QColor(0xFF, 0x00, 0x00),
    "busy":QColor(0xFF, 0x00, 0xFF)
}


from NysaGui.common.nysa_bus_view.wishbone_controller import WishboneController
#Default Project

DEFAULT_CONFIG = {
    "board":"none",
    "IMAGE_ID":0x00,
    "bus_type":"wishbone",
    "TEMPLATE":"wishbone_template.json",
    "INTERFACE":{
    },
    "SLAVES":{
    },
    "MEMORY":{
        "id":0x05,
        "sub_id":0x00,
        "unique_id":0x00,
        "address":0x00,
        "size":0x00000100,
        "device_index, status":0
    }
}


class IBuilderProject(QObject):
    def __init__(self, actions, status, name, path = None):
        super(IBuilderProject, self).__init__()
        self.actions = actions
        self.status = status

        self.project_view = ProjectView(actions, status)


        self.name = QString(name)
        self.path = path
        self.config = None
        if self.path is not None:
            self.load_project()
        else:
            self.config_dict = copy.deepcopy(DEFAULT_CONFIG)
        self.project_status = "unsaved"
        self.controller = WishboneController(self.config_dict,
                                            self.project_view.get_designer_scene(),
                                            self.status)

    def get_view_names(self):
        return self.project_view.get_view_names()

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_path(self):
        return self.path

    def set_path(self, path):
        self.path = path

    def save_project(self):
        self.status.Error("Save Project Not Implemented Yet")

    def load_project(self):
        self.status.Error("Load Project Not Implemented Yet")

    def get_status(self):
        return self.project_status

    def get_status_color(self):
        return PROJECT_STATUS_DICT[self.status]

    def get_view(self):
        return self.project_view

