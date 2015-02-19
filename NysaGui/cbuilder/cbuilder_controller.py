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
#from nysa.cbuilder.scripts.cbuilder_factory import CBuilderFactory
from nysa.ibuilder.lib import utils
from nysa.tools.generate_slave import generate_slave_from_dict

from cbuilder_project import CBuilderProject

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
        self.search_for_projects()

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
        cb["NAME"] = self.wizard.get_core_name()
        cb["ABI_MAJOR"] = self.wizard.get_slave_id()
        cb["ABI_MINOR"] = self.wizard.get_slave_sub_id()
        output_dir = self.wizard.get_output_dir()
        output_dir = os.path.abspath(output_dir)
        self.status.Important("Generating Slave!")
        self.status.Important("Generated Slave at: %s" % output_dir)
        generate_slave_from_dict(cb, output_dir, self.status)

    def search_for_projects(self):
        path = utils.get_user_cbuilder_project_dir()
        self.status.Info("Searching for projects...")
        dirs = self._search_for_projects(path)
        for d in dirs:
            self.status.Info("Found: %s" % d)
            name = os.path.split(d)[-1]
            cp = CBuilderProject(self.actions, self.status, name, d)
            self.view.add_project(cp)

    def _search_for_projects(self, base_dir):
        command_file = "command_file.txt"
        found_dirs = []
        for root, dirs, names in os.walk(base_dir):
            if command_file in names:
                found_dirs.append(os.path.abspath(root))
            for d in dirs:
                found_dirs.extend(self._search_for_projects(d))
        return found_dirs
