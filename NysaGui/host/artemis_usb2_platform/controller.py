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

from artemis_usb2_platform_actions import ArtemisUSB2Actions

from nysa.common import status
from nysa.host import platform_scanner

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))

from nysa_base_controller import NysaBaseController
from artemis_usb2.driver.artemis_usb2_driver import ArtemisUSB2Driver
from view.view import View

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             "common"))


# Put your device name (GPIO, SPI, I2C, etc...)
DRIVER = ArtemisUSB2Driver
APP_NAME = "ArtemisUSB2 Platform"

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
        self.actions = ArtemisUSB2Actions()
        self.actions.artemis_refresh.connect(self.refresh)

        self.actions.pcie_rx_reset.connect(self.pcie_rx_reset)
        self.actions.pcie_rx_polarity.connect(self.pcie_rx_polarity)
        self.actions.pcie_reset.connect(self.pcie_reset)
        self.actions.sata_reset.connect(self.sata_reset)
        self.actions.gtp_preamp_changed.connect(self.gtp_preamp_changed)
        self.actions.gtp_tx_swing_changed.connect(self.gtp_tx_swing_changed)


    def _initialize(self, platform, urn):
        self.v = View(self.status, self.actions)
        self.drv = ArtemisUSB2Driver(platform, urn)
        self.refresh()

    def start_tab_view(self, platform, urn, status):
        self.status = status
        self.status.Verbose( "Starting Template Application")
        self._initialize(platform, urn)

    def get_view(self):
        return self.v

    def refresh(self):
        self.status.Debug("Refresh")
        self.v.set_pcie_rx_reset(self.drv.is_pcie_rx_reset())
        self.v.set_pcie_rx_polarity(self.drv.is_pcie_rx_polarity_positive())
        self.v.set_pcie_reset(self.drv.is_pcie_reset())
        self.v.set_sata_reset(self.drv.is_sata_reset())
        self.v.set_gtp_tx_diff_swing(self.drv.get_gtp_tx_diff_swing())
        self.v.set_gtp_rx_preamp(self.drv.get_gtp_rx_preamp())
        self.v.set_sata_gtp_pll_locked(self.drv.is_sata_pll_locked())
        self.v.set_pcie_gtp_pll_locked(self.drv.is_pcie_pll_locked())
        self.v.set_sata_reset_done(self.drv.is_sata_reset_done())
        self.v.set_pcie_reset_done(self.drv.is_pcie_reset_done())
        self.v.set_sata_dcm_pll_locked(self.drv.is_sata_dcm_pll_locked())
        self.v.set_pcie_dcm_pll_locked(self.drv.is_pcie_dcm_pll_locked())
        self.v.set_sata_rx_idle(self.drv.is_sata_rx_idle())
        self.v.set_pcie_rx_idle(self.drv.is_pcie_rx_idle())
        self.v.set_sata_tx_idle(self.drv.is_sata_tx_idle())
        self.v.set_pcie_tx_idle(self.drv.is_pcie_tx_idle())


    def pcie_rx_reset(self, enable):
        self.drv.enable_pcie_rx_reset(enable)

    def pcie_rx_polarity(self, enable):
        self.drv.set_pcie_rx-polarity(enable)

    def pcie_reset(self, enable):
        self.drv.enable_pcie_reset(enable)

    def sata_reset(self, enable):
        self.drv.enable_sata_reset(enable)

    def gtp_preamp_changed(self, value):
        self.drv.set_gtp_rx_preamp(value)

    def gtp_tx_swing_changed(self, value):
        self.drv.set_gtp_tx_diff_swing(value)


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

