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

from sata_actions import SataActions

from nysa.common import status
from nysa.host import platform_scanner

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))

from nysa_base_controller import NysaBaseController
from nysa.host.driver.sata_driver import SATADriver
from view.view import View

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             "common"))


# Put your device name (GPIO, SPI, I2C, etc...)
DRIVER = SATADriver
APP_NAME = "Sata Platform"

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
        self.actions = SataActions()
        self.actions.sata_refresh.connect(self.refresh)

        self.actions.sata_command_layer_reset.connect         (self.sata_command_layer_reset       )
        self.actions.en_hd_int_changed.connect                (self.en_hd_int_changed              )
        self.actions.en_dma_activate_int_changed.connect      (self.en_dma_activate_int_changed    )
        self.actions.en_d2h_reg_int_changed.connect           (self.en_d2h_reg_int_changed         )
        self.actions.en_pio_setup_int_changed.connect         (self.en_pio_setup_int_changed       )
        self.actions.en_d2h_data_int_changed.connect          (self.en_d2h_data_int_changed        )
        self.actions.en_dma_setup_int_changed.connect         (self.en_dma_setup_int_changed       )
        self.actions.en_set_device_bits_int_changed.connect   (self.en_set_device_bits_int_changed )
        self.actions.sata_reset.connect                       (self.sata_reset                     )
        self.actions.send_hard_drive_command.connect          (self.send_hard_drive_command        )
        self.actions.send_hard_drive_features.connect         (self.send_hard_drive_features       )

    def _initialize(self, platform, urn):
        self.v = View(self.status, self.actions)
        self.drv = SATADriver(platform, urn)
        self.refresh()

    def start_tab_view(self, platform, urn, status):
        self.status = status
        self.status.Verbose( "Starting Template Application")
        self._initialize(platform, urn)

    def get_view(self):
        return self.v

    def refresh(self):
        self.status.Debug("Refresh")
        self.v.enable_sata_reset(self.drv.is_sata_reset())
        self.v.enable_sata_reset_active(self.drv.is_sata_reset_active())
        self.v.enable_command_layer_reset_checkbox(self.drv.is_sata_command_layer_reset())
        self.v.enable_hd_int(self.drv.is_hd_interrupt())
        self.v.enable_dma_activate_int(self.drv.is_dma_activate_stb())
        self.v.enable_d2h_reg_int(self.drv.is_d2h_reg_stb())
        self.v.enable_pio_setup_int(self.drv.is_pio_setup_stb())
        self.v.enable_d2h_data_int(self.drv.is_d2h_data_stb())
        self.v.enable_dma_setup_int(self.drv.is_dma_setup_stb())
        self.v.enable_set_device_bits_int(self.drv.is_set_device_bits_stb())
        self.v.enable_platform_ready(self.drv.is_platform_ready())
        self.v.enable_platform_error(self.drv.is_platform_error())
        self.v.enable_linkup(self.drv.is_linkup())
        self.v.enable_sata_busy(self.drv.is_sata_busy())
        self.v.enable_command_layer_ready(self.drv.is_command_layer_ready())
        self.v.enable_transport_layer_ready(self.drv.is_transport_layer_ready())
        self.v.enable_link_layer_ready(self.drv.is_link_layer_ready())
        self.v.enable_phy_layer_ready(self.drv.is_phy_ready())
        self.v.enable_hard_drive_error(self.drv.is_hard_drive_error())
        self.v.enable_pio_data_ready(self.drv.is_pio_data_ready())
        self.v.enable_d2h_interrupt(self.drv.is_d2h_interrupt())
        self.v.enable_d2h_notification(self.drv.is_d2h_notification())
        self.v.enable_d2h_pmult(self.drv.get_d2h_pmult())
        self.v.enable_d2h_status(self.drv.get_d2h_status())
        self.v.enable_d2h_error(self.drv.get_d2h_error())

        self.v.enable_rx_comm_init_detect(self.drv.get_rx_comm_init_detect())
        self.v.enable_rx_comm_wake_detect(self.drv.get_rx_comm_wake_detect())
        self.v.enable_tx_oob_complete(self.drv.get_tx_oob_complete())
        self.v.enable_tx_comm_reset(self.drv.get_tx_comm_reset())
        self.v.enable_tx_comm_wake(self.drv.get_tx_comm_wake())

        self.v.set_oob_state(self.drv.get_oob_state())
        self.v.set_debug_linkup_data(self.drv.get_debug_linkup_data())
        self.v.set_d2h_lba(self.drv.get_hard_drive_lba())
        self.v.set_d2h_fis(self.drv.get_d2h_fis())

    def sata_reset(self, enable):
        self.drv.enable_sata_reset(enable)

    def sata_command_layer_reset(self, enable):
        self.drv.enable_sata_command_layer_reset(enable)

    def en_hd_int_changed(self, enable):
        self.drv.enable_hd_interrupt(enable)

    def en_dma_activate_int_changed(self, enable):
        self.drv.enable_dma_activate_stb(enable)

    def en_d2h_reg_int_changed(self, enable):
        self.enable_d2h_reg_stb(enable)

    def en_pio_setup_int_changed(self, enable):
        self.enable_d2h_reg_stb(enable)

    def en_d2h_data_int_changed(self, enable):
        self.enable_d2h_data_stb(enable)

    def en_dma_setup_int_changed(self, enable):
        self.enable_dma_setup_stb(enable)

    def en_set_device_bits_int_changed(self, enable):
        self.enable_set_device_bits_set(enable)

    def send_hard_drive_features(self, features):
        self.drv.send_hard_drive_features(features)

    def send_hard_drive_command(self, command):
        self.status.Info("Sending Command: 0x%02X" % command)
        self.drv.send_hard_drive_command(command)


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

