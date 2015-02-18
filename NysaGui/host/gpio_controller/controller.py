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
app template controller
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import argparse
import time

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qt import *

from nysa.common import status
from nysa.host.nysa import Nysa
from nysa.host.driver.gpio import GPIO
from nysa.host.platform_scanner import get_platforms_with_device
from nysa.host import platform_scanner

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))

from nysa_base_controller import NysaBaseController

from view.gpio_widget import GPIOWidget

DRIVER = GPIO
APP_NAME = "GPIO Controller"

#Module Defines
n = str(os.path.split(__file__)[1])

DESCRIPTION = "\n" \
"\n"\
"GPIO Controller\n"

EPILOG = "\n" \
"\n"\
"Examples:\n"\
"\tDebug\n" \
"\t\t%s -d\n"\
"\n" % n

from gpio_actions import GPIOActions

class Controller(NysaBaseController):

    @staticmethod
    def get_name():
        return APP_NAME

    @staticmethod
    def get_driver():
        return DRIVER

    def __init__(self):
        super (Controller, self).__init__()
        self.gpio_actions = GPIOActions()
        self.gpio_actions.get_pressed.connect(self.register_get_pressed)
        self.gpio_actions.set_pressed.connect(self.register_set_pressed)
        self.gpio_actions.gpio_out_changed.connect(self.gpio_out_changed)
        self.gpio_actions.direction_changed.connect(self.direction_changed)
        self.gpio_actions.interrupt_en_changed.connect(self.interrupt_en_changed)
        self.gpio_actions.interrupt_edge_changed.connect(self.interrupt_edge_changed)
        self.gpio_actions.interrupt_both_edge_changed.connect(self.interrupt_both_edge_changed)
        self.gpio_actions.read_start_stop.connect(self.read_start_stop)
        self.gpio_actions.gpio_input_changed.connect(self.gpio_input_changed)
        self.gpio_actions.gpio_interrupt.connect(self.process_interrupts)

    def _initialize(self, platform, urn):
        self.v = GPIOWidget(count = 32, gpio_actions = self.gpio_actions)
        self.gpio = GPIO(platform, urn, debug = False)

        #Initialize the thread with a 40mS timeout
        self.v.add_register(0, "Value", initial_value = self.gpio.get_port_raw())
        self.v.add_register(1, "Direction", initial_value = self.gpio.get_port_direction())
        self.v.add_register(2, "Interrupts", initial_value = self.gpio.get_interrupts())
        self.v.add_register(3, "Interrupt Enable", initial_value = self.gpio.get_interrupt_enable())
        self.v.add_register(4, "Interrupt Edge", initial_value = self.gpio.get_interrupt_edge())
        self.v.add_register(5, "Interrupt Both Edge", initial_value = self.gpio.get_interrupt_both_edge())
        self.v.add_register(6, "Interrupt Timeout", initial_value = self.gpio.get_interrupt_timeout())
        self.v.add_register(7, "Read Clock Rate", initial_value = self.gpio.get_clock_rate())
        self.gpio.register_interrupt_callback(self.interrupt_callback)

    def start_tab_view(self, platform, urn, status):
        self.status = status
        self.status.Verbose("Thread name: %s" % QThread.currentThread().objectName())
        self._initialize(platform, urn)

    def get_view(self):
        return self.v

    def read_start_stop(self, start_stop, rate):
        self.status.Verbose("Enter Read/startstop")

    def gpio_input_changed(self, value):
        self.status.Verbose("Input Changed")
        #Input Changed
        self.v.set_register(0, value)

    def register_get_pressed(self, index):
        self.status.Verbose("Register Get Pressed: %d" % index)
        value = self.gpio.read_register(index)
        self.v.set_register(index, value)

    def register_set_pressed(self, index, value):
        self.status.Verbose("Register Set Pressed: %d: %d" % (index, value))
        self.gpio.write_register(index, value)

    def gpio_out_changed(self, index, val):
        self.status.Verbose( "GPIO Out: %d : %s" % (index, str(val)))
        self.gpio.set_bit_value(index, val)

    def direction_changed(self, index, value):
        self.status.Verbose( "GPIO Direction: %d : %s" % (index, str(value)))
        self.gpio.enable_register_bit(1, index, value)

    def interrupt_en_changed(self, index, value):
        self.status.Verbose("Interrupt En Changed: %d : %s" % (index, str(value)))
        self.gpio.enable_register_bit(3, index, value)

    def interrupt_edge_changed(self, index, value):
        self.status.Verbose("Interrupt Edge Changed %d : %s" % (index, str(value)))
        self.gpio.enable_register_bit(4, index, value)

    def interrupt_both_edge_changed(self, index, value):
        self.status.Verbose("Interrupt Both Edges Changed %d: %s" % (index, str(value)))
        self.gpio.enable_register_bit(5, index, value)

    def process_interrupts(self):
        self.status.Verbose("Process interrupts")
        value = self.gpio.get_port_raw()
        interrupts = self.gpio.get_interrupts()
        self.v.set_register(2, interrupts)
        self.gpio_actions.gpio_input_changed.emit(value)

    def interrupt_callback(self):
        self.status.Verbose("Received interrupt callback")
        self.gpio_actions.gpio_interrupt.emit()

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

