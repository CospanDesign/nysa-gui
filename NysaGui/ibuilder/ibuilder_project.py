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

from ibuilder_project_actions import IBuilderProjectActions
from view.project_view import ProjectView

from nysa.ibuilder.lib import utils
from nysa.ibuilder.lib import verilog_utils as vutils
from nysa.cbuilder.drt import drt

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
        "gpio1":{
            "filename":"wb_gpio.v",
            "unique_id":1,
            "bind":{
                "gpio_out[1:0]":{
                    "loc":"led[1:0]",
                    "direction":"output"
                 },
                "gpio_in[3:2]":{
                    "loc":"button[1:0]",
                    "direction":"input"
                }
            }
        },
        "stpr0":{
            "filename":"wb_stepper.v",
            "bind":{
                "o_hbridge0_l":{
                    "loc":"pmoda7",
                    "direction":"output"
                },
                "o_hbridge0_r":{
                    "loc":"pmoda8",
                    "direction":"output"
                },
                "o_hbridge1_l":{
                    "loc":"pmoda9",
                    "direction":"output"
                },
                "o_hbridge1_r":{
                    "loc":"pmoda10",
                    "direction":"output"
                }
            }
        }
    },
    "MEMORY":{
        "mem1":{
            "id":0x05,
            "sub_id":0x00,
            "unique_id":0x00,
            "address":0x00,
            "size":0x00000100,
            "device_index, status":0
        }
    }
}


class IBuilderProject(QObject):

    def __init__(self, actions, status, name, path = None):
        super(IBuilderProject, self).__init__()
        self.actions = actions
        self.status = status
        self.project_actions = IBuilderProjectActions()

        self.project_view = ProjectView(self.project_actions, status)

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

        self.project_view.set_controller(self.controller)
        #self.project_actions.drag_move_event.connect(self.controller.drag_move)

        self.controller.initialize_view()
        self.controller.enable_editing()
        self.initialize_slave_lists()

    def initialize_slave_lists(self):
        bus_type = self.controller.get_bus()
        paths = utils.get_local_verilog_paths()
        slave_list = utils.get_slave_list(bus_type, paths)

        peripheral_dict = {}
        memory_dict = {}

        for slave in slave_list:
            tags = vutils.get_module_tags(  filename = slave,
                                            keywords=["DRT_FLAGS", "DRT_ID"],
                                            bus = self.controller.get_bus(),
                                            user_paths = paths)
            #print "Tags: %s" % str(tags)
            core_id = int(tags["keywords"]["DRT_ID"])
            if drt.is_memory_core(core_id):
                memory_dict[tags["module"]] = tags
            else:
                peripheral_dict[tags["module"]] = tags

        self.project_actions.setup_peripheral_bus_list.emit(peripheral_dict)
        self.project_actions.setup_memory_bus_list.emit(memory_dict)



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
        return PROJECT_STATUS_DICT[self.project_status]

    def get_view(self):
        return self.project_view

