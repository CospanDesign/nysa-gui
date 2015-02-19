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


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from NysaGui.common.status import Status
from NysaGui.common.status import StatusLevel
from NysaGui.common.xmsgs.xmsgs import Xmsgs

from NysaGui.host.host_controller import HostController
from NysaGui.ibuilder.ibuilder_controller import IBuilderController
from NysaGui.cbuilder.cbuilder_controller import CBuilderController

from view.main_view import MainForm
from actions import Actions


class NysaGui(QObject):
    def __init__(self, debug=False):
        super(NysaGui, self).__init__()
        app = QApplication(sys.argv)
        QThread.currentThread().setObjectName("main")
        self.actions = Actions()
        self.status = Status()
        self.xmsgs = Xmsgs(self.status)

        if debug:
            self.status.set_level(StatusLevel.VERBOSE)

        # Get Host Controller
        self.hc = HostController(self.actions, self.status)
        hv = self.hc.get_view()
        #Get Ibuilder Controller
        self.ic = IBuilderController(self.actions, self.status, self.xmsgs)
        iv = self.ic.get_view()
        #Get CBuilder Controller
        self.cc = CBuilderController(self.actions, self.status)
        cv = self.cc.get_view()

        self.mf = MainForm(self.actions, self.status, self.xmsgs, hv, iv, cv)

        self.status.Debug("Created main form!")
        self.hc.refresh_platform_tree()
        app.exec_()

def main(argv=None):
    n = NysaGui(debug=True)

if __name__ == "__main__":
    main(sys.argv)

