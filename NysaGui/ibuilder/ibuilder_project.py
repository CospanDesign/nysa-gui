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
        self.config_dict["PROJECT_NAME"] = name
        self.project_status = "unsaved"
        self.controller = WishboneController(self.config_dict,
                                            self.project_view.get_designer_scene(),
                                            self.status)

        self.project_view.set_controller(self.controller)
        #self.project_actions.drag_move_event.connect(self.controller.drag_move)

        self.controller.initialize_view()
        self.controller.enable_editing()
        self.initialize_slave_lists()
        self.project_actions.remove_slave.connect(self.controller.remove_slave)
        self.project_actions.internal_bind_connect.connect(self.controller.bind_internal_signal)
        self.project_actions.internal_bind_disconnect.connect(self.controller.unbind_internal_signal)
        self.controller.initialize_constraint_editor(self.project_view.get_constraint_editor())
        self.controller.initialize_configuration_editor(self.project_view.get_configuration_editor())

    def load_project(self):
        self.config_dict = json.load(open(str(self.path), 'r'))
        
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
        #self.project_view.get_designer_scene().view.fit_in_view()

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
        #self.status.Error("Save Project Not Implemented Yet")
        self.controller.model.commit_all_project_tags()
        project_tags = self.controller.get_config_dict()
        #print "project tags:"
        #utils.pretty_print_dict(project_tags)
        initial_dir = utils.get_nysa_user_base()
        initial_dir = os.path.join(initial_dir, "user ibuilder projects")
        print "user base: %s" % initial_dir
        path = os.path.join(initial_dir, project_tags["PROJECT_NAME"])
        file_path = path
        p = path + ".json"
        if not os.path.exists(p):
            file_path = QFileDialog.getSaveFileName(None,
                                            caption = "Select a location to save a project",
                                            directory = path,
                                            filter = "*.json")
        f, e = os.path.splitext(str(file_path))
        if len(e) == 0:
            file_path = "%s.%s" % (file_path, "json")
        if len(file_path) == 0:
            print "cancel"
            return
        print "user path: %s" % file_path
        f = open(file_path, 'w')
        js = None
        try:
            js = json.dumps(project_tags,
                        sort_keys = True,
                        indent = 2,
                        separators=(",", ":"))
        except TypeError as ex:
            print "Error generating json string: %s" % ex
            print "Dumping project tags:"
            utils.pretty_print_dict(project_tags)
            
        f.write(js)
        f.close()

    def get_status(self):
        return self.project_status

    def get_status_color(self):
        return PROJECT_STATUS_DICT[self.project_status]

    def get_view(self):
        return self.project_view


DEFAULT_CONFIG = {
    "BASE_DIR":"~/projects/ibuilder_project",
    "board":"dionysus",
    "IMAGE_ID":256,
    "PROJECT_NAME":"example_project",
    "TEMPLATE":"wishbone_template.json",
    "INTERFACE":{
        "filename":"ft_master_interface.v",
        "bind":{
            "i_ftdi_clk":{
                "loc":"ftdi_clk",
                "direction":"input"
            },
            "io_ftdi_data[7:0]":{
                "loc":"d[7:0]",
                "direction":"inout"
            },
            "i_ftdi_txe_n":{
                "loc":"txe_n",
                "direction":"input"
            },
            "o_ftdi_wr_n":{
                "loc":"wr_n",
                "direction":"output"
            },
            "i_ftdi_rde_n":{
                "loc":"rxe_n",
                "direction":"input"
            },
            "o_ftdi_rd_n":{
                "loc":"rd_n",
                "direction":"output"
            },
            "o_ftdi_oe_n":{
                "loc":"oe_n",
                "direction":"output"
            },
            "o_ftdi_siwu":{
                "loc":"siwua",
                "direction":"output"
            },
            "i_ftdi_suspend_n":{
                "loc":"suspend_n",
                "direction":"input"
            }
        }
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
        }
    },
    "MEMORY":{
        "mem1":{
            "filename":"wb_sdram.v",
            "bind":{
                "o_sdram_clk":{
                    "loc":"sdram_clk",
                    "direction":"output"
                },
                "o_sdram_cke":{
                    "loc":"cke",
                    "direction":"output"
                },
                "o_sdram_cs_n":{
                    "loc":"cs_n",
                    "direction":"output"
                },
                "o_sdram_ras":{
                    "loc":"ras",
                    "direction":"output"
                },
                "o_sdram_cas":{
                    "loc":"cas",
                    "direction":"output"
                },
                "o_sdram_we":{
                    "loc":"we",
                    "direction":"output"
                },
                "o_sdram_bank[1:0]":{
                    "loc":"ba[1:0]",
                    "direction":"output"
                },
                "o_sdram_addr[11:0]":{
                    "loc":"a[11:0]",
                    "direction":"output"
                },
                "io_sdram_data[15:0]":{
                    "loc":"dq[15:0]",
                    "direction":"inout"
                },
                "o_sdram_data_mask[1]":{
                    "loc":"dqmh",
                    "direction":"output"
                },
                "o_sdram_data_mask[0]":{
                    "loc":"dqml",
                    "direction":"output"
                }

            }
        }
    },
    "bind":{
        "clk":{
            "direction":"input",
            "loc":"clk"
        },
        "rst":{
            "direction":"input",
            "loc":"rst"
        }
    },
    "internal_bind":{
        "test_to":"test_from",
        "test_to_2nd":"test_from_2nd"
    },
    "constraint_files":[
        ]
}
