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
adc visualizer controller
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import argparse
from array import array as Array
import numpy as np


from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qt import *

from nysa.common import status
from nysa.host.nysa import Nysa
from nysa.host import platform_scanner

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

#Platform Scanner
sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))

from nysa_base_controller import NysaBaseController
from view.view import View


from nysa.host.driver.i2c import I2C


DRIVER = I2C
APP_NAME = "ADC Visualizer"

#Module Defines
n = str(os.path.split(__file__)[1])

DESCRIPTION = "\n" \
"\n"\
"A I2C ADC Application\n"

EPILOG = "\n" \
"\n"\
"Examples:\n"\
"\tSomething\n" \
"\t\t%s Something\n"\
"\n" % n

from adc_actions import ADCActions

ADC_ADDR = 0x28

class Controller(NysaBaseController):

    def __init__(self):
        super (Controller, self).__init__()
        self.i2c = None
        self.platform_name = None

    def _initialize(self, platform, urn):
        self.v = View(self.status, self.actions)
        self.platform_name = platform.get_board_name()
        #Setup I2C
        self.i2c = I2C(platform, urn)
        if self.platform_name != "sim":
            self.adc_init()

        #Initialize I2C Loop
        self.t = QTimer()
        self.t.timeout.connect(self.update)
        self.t.start(10)
        self.pos = 0

    def adc_init(self):
        self.i2c.reset_i2c_core()
        self.i2c.enable_i2c(True)
        self.i2c.enable_interrupt(True)
        self.i2c.get_status()
        self.i2c.set_speed_to_400khz()
        self.i2c.write_to_i2c(ADC_ADDR, [0x18])

    def update(self):
        #val = np.random.randint(100)
        #print "updating [%d, %d]" % (self.pos, val)
        max_val = self.v.get_time_window()
        max_val = (max_val * 1.0) / 1.5
        value = 0
        if self.platform_name != "sim":
            val = self.i2c.read_from_i2c(ADC_ADDR, [], 2)
            channel_id = (val[0] >> 4) & 0xFF
            value = (((val[0]) & 0x0F) << 8) + (val[1]) * 1.0
            value = value / 4096.0 * 100.0
        else:
            value = (np.sin(2 * np.pi / max_val * (self.pos % int(max_val))) * (max_val / 2)) + (max_val / 2)


        #print "val: %s" % str(val)
        #print "address: %d" % channel_id
        #print "value: %d" % value

        self.v.append_data("demo", self.pos, value)
        self.pos += 1

    def start_tab_view(self, platform, urn, status):
        self.status = status
        self.status.Verbose( "Starting Template Application")
        self._initialize(platform, urn)

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

