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


"""
SDB (Self Defined Bus Viewer)
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import argparse

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qt import *

from nysa.common import status
from nysa.host import platform_scanner

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))

from nysa_base_controller import NysaBaseController
from view.view import View
from model.model import AppModel

DRIVER = SDB
APP_NAME = "Self Defined Bus Viewer"

#Module Defines
n = str(os.path.split(__file__)[1])

DESCRIPTION = "\n" \
"\n"\
"%s\n" % APP_NAME

EPILOG = "\n"

class Controller(NysaBaseController):

    def __init__(self):
        super (Controller, self).__init__()
        f = open(SDB_DESC_LOC, 'r')
        s = f.read()
        f.close()
        s = s.split("DESCRIPTION START")[1]
        s = s.split("DESCRIPTION END")[0]
        #print "s: %s" % s
        self.drt_desc = s
        self.m = AppModel()

    def _initialize(self, platform, urn):
        self.m.setup_model(self, platform)
        self.v = View(self.status, self.actions)
        self.v.setup_simple_text_output_view()
        self.v.clear_text()
        self.v.append_text(self.drt_desc)

        for i in range(self.m.get_row_count()):
            row_data = self.m.get_row_data(i)
            index = "0x%02X" % i
            self.v.add_drt_entry(index, row_data[0], row_data[1], row_data[2], row_data[3])

        self.v.resize_columns()
        self.v.collapse_all()

    def start_tab_view(self, platform, urn, status):
        self.status = status
        self._initialize(platform)

    def get_view(self):
        return self.v

def main():
    #Parse out the commandline arguments
    s = status.Status()
    s.set_level("info")
    parser = argparse.ArgumentParser(
            formatter_class = argparse.RawDescriptionHelpFormatter,
            description = DESCRIPTION,
            epilog = EPILOG
    )
    parser.add_argument("-d", "--debug",
                        action = "store_true",
                        help = "Enable Debug Messages")
    parser.add_argument("platform",
                        type = str,
                        nargs='?',
                        default=["first"],
                        help="Specify the platform to use")

    args = parser.parse_args()

    if args.debug:
        s.set_level("verbose")
        s.Debug("Debug Enabled")

    s.Verbose("platform scanner: %s" % str(dir(platform_scanner)))
    platforms = platform_scanner.get_platforms_with_device(DRIVER, s)

    if len(platforms) == 0:
        sys.exit("Didn't find any platforms with device: %s" % str(DRIVER))

    platform = platforms[0]
    urn = platform.find_device(DRIVER)[0]
    s.Important("Using: %s" % platform.get_board_name())

    #Get a reference to the controller
    c = Controller()

    #Initialize the application
    app = QApplication(sys.argv)
    main = QMainWindow()

    #Tell the controller to set things up
    c.start_tab_view(platform, urn, s)
    QThread.currentThread().setObjectName("main")
    s.Verbose("Thread name: %s" % QThread.currentThread().objectName())
    #Pass in the view to the main widget
    main.setCentralWidget(c.get_view())
    main.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

