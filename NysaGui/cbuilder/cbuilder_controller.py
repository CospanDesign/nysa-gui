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

from PyQt4.Qt import *
from PyQt4.QtCore import *

from view.cbuilder_view import CBuilderView
from cbuilder_actions import Actions
from core_wizard import CoreWizard
from nysa.cbuilder.scripts.cbuilder_factory import CBuilderFactory

class CBuilderController(QObject):
    def __init__(self, actions, status):
        super(CBuilderController, self).__init__()
        self.nysa_gui_actions = actions
        self.actions = Actions()
        self.status = status
        self.view = CBuilderView(self.actions, self.status)
        self.nysa_gui_actions.cbuilder_save.connect(self.save)
        self.nysa_gui_actions.cbuilder_open.connect(self.open)
        self.actions.cbuilder_new_core.connect(self.new_core_wizard)
        self.wizard = None

    def get_view(self):
        return self.view

    def save(self):
        print "cbuilder save"

    def open(self):
        print "cbuilder open"

    def new_core_wizard(self):
        
        self.wizard = CoreWizard(self.actions, self.status)
        self.wizard.accepted.connect(self.wizard_accepted)
        self.wizard.go()

    def wizard_accepted(self):
        cb = {}
        cb["name"] = self.wizard.get_core_name()
        cb["drt_id"] = self.wizard.get_slave_id()
        cb["drt_sub_id"] = self.wizard.get_slave_sub_id()
        cb["drt_flags"] = 1
        cb["drt_size"] = 0
        cb["type"] = self.wizard.get_bus_type()
        cb["bus_type"] = "slave"
        cb["type"] = "wishbone"
        cb["subtype"] = "peripheral"
        output_dir = self.wizard.get_output_dir()
        cb["base"] = os.path.abspath(output_dir)
        dma_reader = self.wizard.is_dma_reader()
        dma_writer = self.wizard.is_dma_writer()
        self.status.Important("Generating Slave!")
        cbuilder = CBuilderFactory(cb)
        self.status.Important("Generated Slave at: %s" % cb["base"])

