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

from nysa.host.platform_scanner import PlatformScanner
from script_manager import ScriptManager
from NysaGui.common.utils import create_hash

from view.host_view import HostView

debug = False

class HostController(QObject):
    def __init__(self, actions, status):
        super(HostController, self).__init__()
        self.actions = actions
        self.status = status
        self.init_ui()
        self.uid = None
        self.config_dict = {}
        self.device_index = None
        self.fv = self.view.get_nysa_bus_view()
        self.scripts = []
        self.sm = ScriptManager(self.status, self.actions)

        self.actions.refresh_signal.connect(self.refresh_platform_tree)
        self.actions.platform_tree_changed_signal.connect(self.platform_changed)

        self.actions.module_selected.connect(self.module_selected)
        self.actions.module_deselected.connect(self.module_deselected)

        self.actions.slave_selected.connect(self.slave_selected)
        self.actions.slave_deselected.connect(self.slave_deselected)

        self.actions.script_item_selected.connect(self.script_item_selected)
        self.actions.remove_tab.connect(self.remove_script)

        self.sm.scan()


    def init_ui(self):
        self.view = HostView(self.actions, self.status)

    def get_view(self):
        return self.view

    def get_nysa_bus_view(self):
        self.view.get_nysa_bus_view()

    def refresh_platform_tree(self):
        self.status.Important("Refresh Platforms")
        self.actions.clear_platform_tree_signal.emit()
        ps = PlatformScanner(self.status)
        platforms_dict = ps.get_platforms()
        
        #print "platform: %s" % str(platforms_dict)
        for platform_name in platforms_dict:
            #platform_name: dionysus
            platform_instance = platforms_dict[platform_name](self.status)
            self.status.Verbose("PF: %s" % platform_instance)
            #platform_uid: platforms_dict[platform_name]: dionysus (nysa class)
            for platform_uid in platform_instance.scan():
                #self.status.Info( "Refresh The Platformsical Tree")
                self.status.Debug("Platform UID: %s" % platform_uid)
                #print "platform_name: %s" % str(platform_name)
                #print "platform_instance: %s" % str(platform_instance)
                #print "platform_uid: %s" % str(platform_uid)
                self.actions.add_device_signal.emit(platform_name, platform_uid, platform_instance)
         
            self.actions.platform_tree_get_first_dev.emit()

    def platform_changed(self, uid, platform_type, nysa_device):
        if self.uid == uid:
            #Don't change anything if it's the same UID
            self.status.Verbose( "Same UID, no change")
            return

        self.status.Debug( "Platform Changed")
        self.platform_type = platform_type
        if platform_type is None:
            self.n = None
            self.status.Info( "No Platform Selected")
            self.fv.clear()
            return

        #print "uid: %s" % str(uid)
        self.uid = uid
        self.n = nysa_device.scan()[str(uid)]

        #print "Nysa: %s" % str(self.n)
        self.n.read_drt()
        self.config_dict = drt_to_config(self.n)
        self.fv.update_nysa_image(self.n, self.config_dict)
        self.setup_bus_properties(self.config_dict, self.n)
        self.device_index = None

    def module_selected(self, name):
        self.status.Verbose( "Module %s Selected" % name)
        self.device_index = None
        self.fv.module_selected(name)
        self.device_index = None

    def module_deselected(self, name):
        self.setup_bus_properties(self.config_dict, self.n)
        self.device_index = None

    def slave_selected(self, name, bus):
        self.status.Info( "Slave: %s on %s bus selected" % (name, bus))
        scripts = []
        #Change the Qt4 String to a normal python string (This is needed
        #for using the OrderedDict

        name = str(name)
        dev_id = None
        dev_sub_id = None
        dev_unique_id = None

        if bus == "Peripherals":
            if name == "DRT":
                dev_id = 0
                dev_sub_id = 0
                unique_id = 0
                self.device_index = 0
            else:

                self.device_index = self.config_dict["SLAVES"][name]["device_index, status"]

                dev_id = self.config_dict["SLAVES"][name]["id"]
                dev_sub_id = self.config_dict["SLAVES"][name]["sub_id"]
                dev_unique_id = self.config_dict["SLAVES"][name]["unique_id"]
        elif bus == "Memory":
            #print "Name: %s" % name
            self.device_index = self.config_dict["MEMORY"][name]["device_index, status"]

            dev_id = self.config_dict["MEMORY"][name]["id"]
            dev_sub_id = self.config_dict["MEMORY"][name]["sub_id"]
            dev_unique_id = self.config_dict["MEMORY"][name]["unique_id"]

        scripts = self.sm.get_device_script(dev_id, dev_sub_id, dev_unique_id)
        self.fv.slave_selected(name, bus, self.config_dict, self.n, scripts)

    def slave_deselected(self, name, bus):
        self.setup_bus_properties(self.config_dict, self.n)
        self.device_index = None

    def setup_bus_properties(self, config_dict, n):
        scripts = []
        image_id = self.config_dict["IMAGE_ID"]
        scripts = self.sm.identify_image_scripts(image_id)
        self.fv.setup_bus_properties(self.uid, self.config_dict, n, scripts)

    def script_item_selected(self, name, script):
        self.status.Debug("Script Item selected: %s: %s" % (name, str(script)))
        #print "UID: %s" % str(self.uid)
        platform = [self.platform_type, self.uid, self.n]
        #print "Script for: %s" % name
        uid = create_hash(self.uid)
        name = "%s:%s" % (self.uid, script.get_name())
        for s in self.scripts:
            if s[0] == uid and s[1] == name:
                return

        widget = script()
        self.scripts.append([uid, name, widget])
        if self.device_index is not None:
            #print "Index: %d" % self.device_index
            widget.start_tab_view(platform, self.device_index, self.status)
        else:
            #print "image ID: %d" % script.get_unique_image_id()
            widget.start_tab_view(platform, self.status)

        view = widget.get_view()
       
        self.view.add_tab(uid, view, name)

    def remove_script(self, view):
        for i in range (len(self.scripts)):
            if view == self.scripts[i][2].get_view():
                del(self.scripts[i])
                return

def drt_to_config(n):
    config_dict = {}
    #Read the board id and find out what type of board this is
    config_dict["board"] = n.get_board_name()
    config_dict["IMAGE_ID"] = n.get_image_id()
    #print "Name: %s" % config_dict["board"]

    #Read the bus flag (Wishbone or Axie)
    if n.is_wishbone_bus():
        config_dict["bus_type"] = "wishbone"
        config_dict["TEMPLATE"] = "wishbone_template.json"
    if n.is_axie_bus():
        config_dict["bus_type"] = "axie"
        config_dict["TEMPLATE"] = "axie_template.json"

    config_dict["SLAVES"] = collections.OrderedDict()
    config_dict["MEMORY"] = collections.OrderedDict()
    #Read the number of slaves
    #Go thrugh each of the slave devices and find out what type it is
    #n.pretty_print_drt()
    #print "Number of devices: %d" % n.get_number_of_devices()
    #Add the DRT to the config


    for i in range (n.get_number_of_devices()):
        if n.is_memory_device(i):
            name = "Memory %d" % i
            #print "Name: %s" % n.get_device_name_from_id(n.get_device_id(i))
            config_dict["MEMORY"][name] = {}
            config_dict["MEMORY"][name]["id"] = n.get_device_id(i)
            config_dict["MEMORY"][name]["sub_id"] = n.get_device_sub_id(i)
            config_dict["MEMORY"][name]["unique_id"] = n.get_device_unique_id(i)
            config_dict["MEMORY"][name]["address"] = n.get_device_address(i)
            config_dict["MEMORY"][name]["size"] = n.get_device_size(i)
            config_dict["MEMORY"][name]["device_index, status"] = i
            continue

        name = n.get_device_name_from_id(n.get_device_id(i))
        name = "%s %d" % (name, i)
        config_dict["SLAVES"][name] = {}
        config_dict["SLAVES"][name]["device_index, status"] = i
        #print "Name: %s" % n.get_device_name_from_id(n.get_device_id(i))
        config_dict["SLAVES"][name]["id"] = n.get_device_id(i)
        config_dict["SLAVES"][name]["sub_id"] = n.get_device_sub_id(i)
        config_dict["SLAVES"][name]["unique_id"] = n.get_device_unique_id(i)
        config_dict["SLAVES"][name]["address"] = n.get_device_address(i)
        config_dict["SLAVES"][name]["size"] = n.get_device_size(i)

    config_dict["INTERFACE"] = {}
    return config_dict
    #Read the number of memory devices



