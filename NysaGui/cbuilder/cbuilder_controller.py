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

from NysaGui.common.gui_utils import create_hash
from view.cbuilder_view import CBuilderView

class CBuilderController(QObject):
    def __init__(self, actions, status):
        super(CBuilderController, self).__init__()
        self.nysa_gui_actions = actions
        self.actions = actions
        #self.actions = Actions()
        self.status = status
        self.view = CBuilderView(self.actions, self.status)
        self.nysa_gui_actions.cbuilder_save.connect(self.save)
        self.nysa_gui_actions.cbuilder_open.connect(self.open)

    def get_view(self):
        return self.view

    def save(self):
        print "cbuilder save"

    def open(self):
        print "cbuilder open"
