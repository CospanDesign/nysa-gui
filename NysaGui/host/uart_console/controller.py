#! /usr/bin/python

# Copyright (c) 2014 Cospan Design LLC (dave.mccoy@cospandesign.com)

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
UART Console
"""

import os
import sys
import argparse
import time
import string
from array import array as Array

import importlib

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qt import *

from nysa.common import status
from nysa.host import platform_scanner

from uart_actions import UARTActions

#App Template
sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))

from nysa_base_controller import NysaBaseController

#Nysa Imports
from nysa.host.driver.uart import UART

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             "common"))

from view.uart_widget import UARTWidget

DRIVER = UART
APP_NAME = "UART Console"

#Module Defines
script_name = str(os.path.split(__file__)[1])

DESCRIPTION = "\n" \
"\n"\
"%s\n" % APP_NAME

EPILOG = "\n" \
"\n"\
"Examples:\n"\
"\tSomething\n" \
"\t\t%s Something\n"\
"\n" % script_name

class Controller(NysaBaseController):

    @staticmethod
    def get_name():
        return APP_NAME

    @staticmethod
    def get_driver():
        return DRIVER

    def __init__(self):
        super (Controller, self).__init__()
        self.uart = None
        self.actions = UARTActions()
        self.actions.uart_baudrate_change.connect(self.baudrate_change)
        self.actions.uart_flowcontrol_change.connect(self.flowcontrol_change)
        self.actions.uart_data_out.connect(self.uart_data_out)
        self.actions.uart_read_data.connect(self.uart_read_data)

    def _initialize(self, platform, urn):
        self.uart = UART(platform, urn, status)
        self.v = UARTWidget(self.status, self.actions)

        #Setup the UART
        self.uart.set_baudrate(self.v.get_baudrate())
        self.flowcontrol_change(self.v.get_flowcontrol())
        data = self.uart.read_all_data()
        #self.v.append_text(data.tostring())
        self.v.append_text(data.tostring())
        self.uart.disable_interrupts()

        self.uart.unregister_interrupt_callback(None)
        self.uart.register_interrupt_callback(self.interrupt_callback)

        self.uart.enable_read_interrupt()

    @pyqtSlot()
    def interrupt_callback(self):
        self.actions.uart_read_data.emit()

    def start_tab_view(self, platform, urn, status):
        self.status = status
        self._initialize(platform, urn)

    def get_view(self):
        return self.v

    def uart_data_out(self, data):
        if self.uart is None:
            return
        #d = Array('B')
        #d.fromstring(data)
        #print "data: %s" % str(d)
        if len(data) > 0:
            data = string.replace(data, "\n", "\r\n")
            self.uart.write_string(data)
            #if d[0] == 13:
            #    self.uart.write_byte(10)

    def uart_read_data(self):
        #self.uart.disable_read_interrupt()
        #data = self.uart.read_all_data()
        data = self.uart.read_string()
        print "final data string: %s" % data
        self.uart.get_status()
        self.v.append_text(data)
        #self.uart.enable_read_interrupt()

    def baudrate_change(self, baudrate):
        self.uart.set_baudrate(baudrate)

    def flowcontrol_change(self, flowcontrol):
        flowcontrol = str(flowcontrol)
        if flowcontrol.lower() == "none":
            self.uart.disable_flowcontrol()

        elif flowcontrol.lower() == "soft":
            self.uart.enable_soft_flowcontrol()

        elif flowcontrol.lower() == "hardware":
            self.uart.enable_hard_flowcontrol()

        self.uart.enable_hard_flowcontrol()

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

