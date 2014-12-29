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

from PyQt4.Qt import QApplication
from PyQt4 import QtCore
from PyQt4 import QtGui

from nysa.host.nysa import Nysa

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


from nysa.common import site_manager
from nysa.common import status
from nysa.host import platform_scanner
from nysa.host.platform_scanner import PlatformScanner
from nysa.host.driver.i2c import I2C

import status
import numpy as np

#Module Defines
n = str(os.path.split(__file__)[1])

DESCRIPTION = "\n" \
"\n"\
"A template app\n"

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

    @staticmethod
    def get_name():
        #Change this for your app
        return "app_template"

    def _initialize(self, platform, device_index):
        self.v = View(self.status, self.actions)
        #Setup I2C
        #self.i2c = I2C(platform[2], device_index, self.status)
        self.i2c = I2C(platform[2], device_index)
        self.adc_init()

        #Initialize I2C Loop
        self.t = QtCore.QTimer()
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
        #max_val = self.v.get_time_window()
        #max_val = (max_val * 1.0) / 1.5
        #val = (np.sin(2 * np.pi / max_val * (self.pos % int(max_val))) * (max_val / 2)) + (max_val / 2)
        val = self.i2c.read_from_i2c(ADC_ADDR, [], 2)
        channel_id = (val[0] >> 4) & 0xFF
        value = (((val[0]) & 0x0F) << 8) + (val[1]) * 1.0
        value = value / 4096.0 * 100.0

        #print "val: %s" % str(val)
        #print "address: %d" % channel_id
        #print "value: %d" % value

        self.v.append_data("demo", self.pos, value)
        self.pos += 1

    def start_standalone_app(self, platform, device_index, status, debug = False):
        app = QApplication (sys.argv)
        main = QtGui.QMainWindow()

        self.status = status.Status()
        if debug:
            self.status.set_level(status.StatusLevel.VERBOSE)
        else:
            self.status.set_level(status.StatusLevel.INFO)
        self.status.Verbose("Starting Standalone Application")
        self._initialize(platform, device_index)
        main.setCentralWidget(self.v)
        main.show()
        sys.exit(app.exec_())

    def start_tab_view(self, platform, device_index, status):
        self.status = status
        self.status.Verbose( "Starting Template Application")
        self._initialize(platform, device_index)

    def get_view(self):
        return self.v

    @staticmethod
    def get_unique_image_id():
        """
        If this ia controller for an entire image return the associated unique
        image ID here
        """
        return None

    @staticmethod
    def get_device_id():
        """
        If this is a controller for an individual device (GPIO, I2C, UART,
        etc...) return the associted device ID here (notes for the device are in
        /nysa/cbuilder/drt/drt.json
        """
        return None

    @staticmethod
    def get_device_sub_id():
        """
        If this is a controller for an individual device with that has a
        specific implementation (Cospan Design's version of a GPIO controller
        as apposed to just a generic GPIO controller) return the sub ID here
        """
        return None

    @staticmethod
    def get_device_unique_id():
        """
        Used to differentiate devices with the same device/sub ids.
        """
        return None


def main(argv):
    #Parse out the commandline arguments
    s = status.Status()
    s.set_level(status.StatusLevel.INFO)
    parser = argparse.ArgumentParser(
            formatter_class = argparse.RawDescriptionHelpFormatter,
            description = DESCRIPTION,
            epilog = EPILOG
    )
    debug = False

    parser.add_argument("-d", "--debug",
                        action = "store_true",
                        help = "Enable Debug Messages")
    parser.add_argument("-l", "--list",
                        action = "store_true",
                        help = "List the available devices from a platform scan")
    parser.add_argument("platform",
                        type = str,
                        nargs='?',
                        default=["first"],
                        help="Specify the platform to use")
 
    args = parser.parse_args()
    plat = ["", None, None]

    if args.debug:
        s.set_level(status.StatusLevel.VERBOSE)
        s.Debug("Debug Enabled")
        debug = True

    pscanner = PlatformScanner()
    platform_dict = pscanner.get_platforms()
    platform_names = platform_dict.keys()
    if "sim" in platform_names:
        #If sim is in the platforms, move it to the end
        platform_names.remove("sim")
        platform_names.append("sim")
    dev_index = None
    for platform_name in platform_dict:
        s.Verbose("Platform: %s" % str(platform_name))
        s.Verbose("Type: %s" % str(platform_dict[platform_name]))

        platform_instance = platform_dict[platform_name](s)
        s.Verbose("Platform Instance: %s" % str(platform_instance))


        instances_dict = platform_instance.scan()
        if plat[1] is not None:
            break
        
        for name in instances_dict:

            #s.Verbose("Found Platform Item: %s" % str(platform_item))
            n = instances_dict[name]
            plat = ["", None, None]
            
            if n is not None:
                s.Verbose("Found a nysa instance: %s" % name)
                n.read_drt()
                #XXX: Put your device name here!
                dev_index = n.find_device(Nysa.get_id_from_name("I2C"))
                if dev_index is not None:
                    s.Important("Found a device at %d" % dev_index)
                    plat = [platform_name, name, n]
                    break
                continue

            if platform_name == args.platform and plat[0] != args.platform:
                #Found a match for a platfom to use
                plat = [platform_name, name, n]
                continue

            s.Verbose("\t%s" % psi)

    if args.list:
        s.Verbose("Listed all platforms, exiting")
        sys.exit(0)

    if plat is not None:
        s.Important("Using: %s" % plat)
    else:
        s.Fatal("Didn't find a platform to use!")


    c = Controller()
    if dev_index is None:
        sys.exit("Failed to find an LCD Device")

    c.start_standalone_app(plat, dev_index, status, debug)

if __name__ == "__main__":
    main(sys.argv)

