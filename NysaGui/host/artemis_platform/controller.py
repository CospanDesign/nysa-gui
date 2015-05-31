#! /usr/bin/python

# Copyright (c) 2015 name (email@example.com)

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
app template controller
"""

__author__ = 'email@example.com (name)'

import os
import sys
import argparse

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qt import *

from artemis_platform_actions import ArtemisActions

from nysa.common import status
from nysa.host import platform_scanner

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))

from nysa_base_controller import NysaBaseController
from artemis.driver.artemis_driver import ArtemisDriver
from view.view import View

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             "common"))


# Put your device name (GPIO, SPI, I2C, etc...)
DRIVER = ArtemisDriver
APP_NAME = "Artemis Platform"

#Module Defines
n = str(os.path.split(__file__)[1])

DESCRIPTION = "\n" \
"\n"\
"%s\n" % APP_NAME

EPILOG = "\n" \
"\n"\
"Examples:\n"\
"\tSomething\n" \
"\t\t%s Something\n"\
"\n" % n


class Controller(NysaBaseController):

    @staticmethod
    def get_name():
        return APP_NAME

    @staticmethod
    def get_driver():
        return DRIVER

    def __init__(self):
        super (Controller, self).__init__()
        self.actions = ArtemisActions()
        self.actions.artemis_refresh.connect(self.refresh)

    def _initialize(self, platform, urn):
        self.v = View(self.status, self.actions)
        self.drv = ArtemisDriver(platform, urn)
        self.refresh()

    def start_tab_view(self, platform, urn, status):
        self.status = status
        self.status.Verbose( "Starting Template Application")
        self._initialize(platform, urn)

    def get_view(self):
        return self.v

    def refresh(self):
        self.v.set_ddr3_reset(self.drv.is_ddr3_rst())
        self.v.set_ddr3_calibration_done(self.drv.is_ddr3_calibration_done())
        self.v.set_main_pll_locked(self.drv.is_main_pll_locked())
        channels = 6
        channel_en = self.drv.get_ddr3_channel_enable()
        for i in range (channels):
            channel_status = self.drv.get_ddr3_channel_status(i)
            self.v.set_channel_enable(i, self.drv.static_is_ddr3_channel_enable(channel_en, i))
            self.v.set_channel_status(i,
                                        self.drv.static_is_ddr3_channel_rd_full(channel_status),
                                        self.drv.static_is_ddr3_channel_rd_empty(channel_status),
                                        self.drv.static_is_ddr3_channel_rd_overflow(channel_status),
                                        self.drv.static_is_ddr3_channel_rd_error(channel_status),
                                        self.drv.static_is_ddr3_channel_wr_empty(channel_status),
                                        self.drv.static_is_ddr3_channel_wr_full(channel_status),
                                        self.drv.static_is_ddr3_channel_wr_underrun(channel_status))

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

