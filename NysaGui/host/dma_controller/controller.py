#! /usr/bin/python

# Copyright (c) 2015 name (dave.mccoy@cospandesign.com)

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
DMA Controller
"""

__author__ = 'dave.mccoy@cospandesign.com (name)'

import os
import sys
import argparse

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qt import *

from nysa.common import status
from nysa.host import platform_scanner
from nysa.host.driver.dma import DMA
from dma_controller_actions import DMAControllerActions

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))

from nysa_base_controller import NysaBaseController
from view.view import View

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             "common"))


# Put your device name (GPIO, SPI, I2C, etc...)
DRIVER = DMA
APP_NAME = "DMA Controller"

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
        self.actions = DMAControllerActions()
        self.actions.source_commit.connect(self.source_commit)
        self.actions.sink_commit.connect(self.sink_commit)
        self.actions.instruction_commit.connect(self.instruction_commit)
        self.actions.enable_dma.connect(self.enable_dma)
        self.actions.channel_enable.connect(self.channel_enable)

    def _initialize(self, platform, urn):
        self.v = View(self.status, self.actions)
        self.dma = DMA(platform, urn)
        self.dma.setup()
        #Keep the DMA Always On
        self.enable_dma(True)
        if platform.get_board_name() == "sim":
            self.dma.channel_count = 4
            self.dma.sink_count = 4
        self.v.setup(self.dma.get_channel_count(), self.dma.get_instruction_count(), self.dma.get_sink_count())
        self.update_view()

    def update_view(self):
        source_count = self.dma.get_channel_count()
        sink_count = self.dma.get_sink_count()
        inst_count = self.dma.get_instruction_count()

        for i in range(source_count):
            sd = {}
            sd["SINK_ADDR"] = self.dma.get_channel_sink_addr(i)
            sd["INC_ADDR"] = self.dma.is_source_address_increment(i)
            sd["DEC_ADDR"] = self.dma.is_source_address_decrement(i)
            self.v.update_source_settings(i, sd)

        for i in range(inst_count):
            inst_dict = {}
            inst_dict["SRC_RST_ON_CMD"] = self.dma.is_instruction_src_addr_reset_on_cmd(i)
            inst_dict["DEST_RST_ON_CMD"] = self.dma.is_instruction_dest_addr_reset_on_cmd(i)
            inst_dict["CMD_CONTINUE"] = self.dma.is_instruction_continue(i)
            inst_dict["EGRESS_ADDR"] = self.dma.get_instruction_egress(i)
            inst_dict["EGRESS_ENABLE"] = self.dma.is_egress_bond(i)
            inst_dict["INGRESS_ADDR"] = self.dma.get_instruction_ingress(i)
            inst_dict["INGRESS_ENABLE"] = self.dma.is_ingress_bond(i)
            inst_dict["SRC_ADDR"] = self.dma.get_instruction_source_address(i)
            inst_dict["DEST_ADDR"] = self.dma.get_instruction_dest_address(i)
            inst_dict["COUNT"] = self.dma.get_instruction_data_count(i)
            self.v.update_instruction_settings(i, inst_dict)

        for i in range(sink_count):
            sink_dict = {}
            sink_dict["INC_ADDR"] = self.dma.is_dest_address_increment(i)
            sink_dict["DEC_ADDR"] = self.dma.is_dest_address_decrement(i)
            sink_dict["RESPECT_QUANTUM"] = self.dma.is_dest_respect_quantum(i)
            self.v.update_sink_settings(i, sink_dict)

    def start_tab_view(self, platform, urn, status):
        self.status = status
        self.status.Verbose( "Starting Template Application")
        self._initialize(platform, urn)

    def get_view(self):
        return self.v

    def source_commit(self, index, source_dict):
        self.dma.set_channel_sink_addr(index, source_dict["SINK_ADDR"])
        self.dma.enable_source_address_increment(index, source_dict["INC_ADDR"])
        self.dma.enable_source_address_decrement(index, source_dict["DEC_ADDR"])
        self.status.Important("Setting up Source: %d"% index)

    def sink_commit(self, index, sink_dict):
        self.dma.enable_dest_address_increment(index, sink_dict["INC_ADDR"])
        self.dma.enable_dest_address_decrement(index, sink_dict["DEC_ADDR"])
        self.dma.enable_dest_respect_quantum(index, sink_dict["RESPECT_QUANTUM"])
        self.status.Important("Setting up Sink: %d" % index)

    def instruction_commit(self, index, inst_dict):
        self.dma.enable_instruction_src_addr_reset_on_cmd(index, inst_dict["SRC_RST_ON_CMD"])
        self.dma.enable_instruction_dest_addr_reset_on_cmd(index, inst_dict["DEST_RST_ON_CMD"])
        self.dma.enable_instruction_continue(index, inst_dict["CMD_CONTINUE"])
        self.dma.set_instruction_egress(index, inst_dict["EGRESS_ADDR"])
        self.dma.enable_egress_bond(index, inst_dict["EGRESS_ENABLE"])
        self.dma.set_instruction_ingress(index, inst_dict["INGRESS_ADDR"])
        self.dma.enable_ingress_bond(index, inst_dict["INGRESS_ENABLE"])
        self.dma.set_instruction_source_address(index, inst_dict["SRC_ADDR"])
        self.dma.set_instruction_dest_address(index, inst_dict["DEST_ADDR"])
        self.dma.set_instruction_data_count(index, inst_dict["COUNT"])
        self.status.Important("Setting up Instruction: %d" % index)

    def enable_dma(self, enable):
        self.dma.enable_dma(enable)

    def channel_enable(self, index, enable):
        self.dma.enable_channel(index, enable)

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

