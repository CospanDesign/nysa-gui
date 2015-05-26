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


""" script manager

Used to manage the different user scripts that can be used within Nysa Viewer
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os
import inspect

from PyQt4.Qt import QObject

p = os.path.join(os.path.dirname(__file__),
                 os.pardir,
                 "common")

p = os.path.abspath(p)
#print ("Path: %s" % p)
sys.path.append(p)

p = os.path.join(os.path.dirname(__file__),
                 os.pardir,
                 os.pardir)

from nysa_base_controller import NysaBaseController


#Declare a QObect subclass in order to take advantage of signals
class ScriptManager(QObject):

    def __init__(self, status, actions):
        super (ScriptManager, self).__init__()
        p = os.path.join(os.path.dirname(__file__),
                         os.pardir)
        self.status = status
        self.actions = actions
        self.script_dirs = [p]
        self.scripts = []

    def scan(self):
        from NysaGui.host.sdb_viewer.controller import Controller as sdb_controller
        from NysaGui.host.gpio_controller.controller import Controller as gpio_controller
        from NysaGui.host.memory_controller.controller import Controller as mem_controller
        from NysaGui.host.i2c_controller.controller import Controller as i2c_controller
        from NysaGui.host.sf_camera_controller.controller import Controller as sf_controller
        from NysaGui.host.uart_console.controller import Controller as uart_controller
        from NysaGui.host.stepper_controller.controller import Controller as stepper_controller
        from NysaGui.host.video_controller.controller import Controller as video_controller
        from NysaGui.host.audio_controller.controller import Controller as audio_controller
        from NysaGui.host.adc_visualizer.controller import Controller as adc_controller
        from NysaGui.host.spi_oled_controller.controller import Controller as oled_controller
        from NysaGui.host.register_viewer.controller import Controller as register_viewer_controller
        from NysaGui.host.dma_controller.controller import Controller as dma_controller
        try:
            from NysaGui.host.artemis_platform.controller import Controller as artemis_driver
        except ImportError:
            self.status.Warning("Artemis Platform was not found")
            pass
        #print "DIR: %s" % (str(dir(self)))
        #self.status.Debug("Directory: %s" % str(dir(self)))

        script_list = NysaBaseController.plugins
        #print "\tNBC CLASSES: %s" % str(NysaBaseController.plugins)
        #self.status.Debug("NBC Class: %s" % str(NysaBaseController.plugins))
        for script in script_list:
            #print "Adding: %s" % str(script)
            self.status.Important("Adding: %s" % str(script))
            self.insert_script(script)

    def insert_script(self, script):
        #Go through the script to see what it interfaces with
        name = script.get_name()
        driver = script.get_driver()
        s = [None, None, None]
        s = {}
        s["name"] = name
        s["driver"] = driver
        s["script"] = script
        self.scripts.append(s)

    def get_device_script(self, abi_class, abi_major, abi_minor, vendor_id, device_id, version, date):
        script_dict = {}
        #print "Number of scripts: %d" % len(self.scripts)
        for script in self.scripts:
            driver = script["driver"]
            if driver.get_abi_class() is not None:
                #print "comparing: %d with %d" % (driver.get_abi_class(), abi_class)
                if driver.get_abi_class() != abi_class:
                    continue
                #print "Pass!"

            if driver.get_abi_major() is not None:
                #print "comparing: %d with %d" % (driver.get_abi_major(), abi_major)
                if driver.get_abi_major() != abi_major:
                    continue
                #print "Pass!"

            if driver.get_abi_minor() is not None:
                if driver.get_abi_minor() != abi_minor:
                    continue

            if driver.get_vendor_id() is not None:
                if driver.get_vendor_id() != vendor_id:
                    continue

            if driver.get_device_id() is not None:
                if driver.get_device_id() != device_id:
                    continue

            if driver.get_version() is not None:
                if driver.get_version() != version:
                    continue

            if driver.get_date() is not None:
                if driver.get_date() != date:
                    continue

            print "Found: %s" % script["name"]
            script_dict[script["name"]] = script["script"]

        return script_dict





