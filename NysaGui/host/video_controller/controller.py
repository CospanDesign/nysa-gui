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
Video Playback controller
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
from nysa.host.driver.lcd_SSD1963 import LCDSSD1963

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

#Platform Scanner
sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))

from nysa_base_controller import NysaBaseController
from video_actions import VideoActions
from view.view import View


from nysa.common import site_manager
from nysa.common import status
from nysa.host import platform_scanner
from nysa.host.platform_scanner import PlatformScanner
import status

#Module Defines
n = str(os.path.split(__file__)[1])



DESCRIPTION = "\n" \
"\n"\
"Playback of media\n"

EPILOG = "\n" \
"\n"\
"Examples:\n"\
"\tSomething\n" \
"\t\t%s Something\n"\
"\n" % n


class Controller(NysaBaseController):

    def __init__(self):
        super (Controller, self).__init__()
        self.actions = VideoActions()
        self.actions.color_test.connect(self.color_test)

    @staticmethod
    def get_name():
        return "Video Viewer"

    def _initialize(self, platform, device_index):
        self.v = View(self.actions, self.status)
        self.platform_name = platform[0]
        self.status.Verbose("Platform Name: %s" % self.platform_name)
        self.lcd = LCDSSD1963(platform[2], device_index, debug = True)

        self.lcd.setup()
        

    def color_test(self):
        if self.platform_name == "sim":
            self.status.Important("Cannot test color test on sim platform")
            return
            
        width = self.lcd.get_image_width()
        height = self.lcd.get_image_height()
        size = width * height
        print "Image Width: %d" % width
        print "Image Height: %d" % height
        print "Total Size: %d" % size
        print "Total Size: 0x%08X" % size
        #Write a color to memory
        red = 0x00FF0000
        green = 0x0000FF00
        blue = 0x000000FF
        cyan = 0x0000FFF0
        purple = 0x00F000FF
        orange = 0x00FFF000
        pink = 0x00FF7070

        color = cyan
        image0 = Array('B')
        for i in range(size):
            image0.append((color >> 24) & 0xFF)
            image0.append((color >> 16) & 0xFF)
            image0.append((color >> 8) & 0xFF)
            image0.append(color & 0xFF)



        color = purple
        image1 = Array('B')
        for i in range(size):
            image1.append((color >> 24) & 0xFF)
            image1.append((color >> 16) & 0xFF)
            image1.append((color >> 8) & 0xFF)
            image1.append(color & 0xFF)


        
        color = pink
        image2 = Array('B')
        for i in range(size):
            image2.append((color >> 24) & 0xFF)
            image2.append((color >> 16) & 0xFF)
            image2.append((color >> 8) & 0xFF)
            image2.append(color & 0xFF)


        color = orange
        image3 = Array('B')
        for i in range(size):
            image3.append((color >> 24) & 0xFF)
            image3.append((color >> 16) & 0xFF)
            image3.append((color >> 8) & 0xFF)
            image3.append(color & 0xFF)


        self.lcd.dma_writer.write(image0)
        self.lcd.dma_writer.write(image1)
        self.lcd.dma_writer.write(image2)
        self.lcd.dma_writer.write(image3)

        #print "Read Command Register"
        #command_register = self.lcd.read_command(0x01, 2)

        #print "Command Register: ",
        #for v in command_register:
        #    print "0x%02X" % v,

        #print ""

        #print "Write Command Register"
        #self.lcd.write_command(0x01, Array('B', [0x01, 0x00]))


        #command_register = self.lcd.read_command(0x01, 2)

        #print "Command Register: ",
        #for v in command_register:
        #    print "0x%02X" % v,

        #print ""


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
        self.status.Verbose("Starting Video Application")
        self._initialize(platform, device_index)

    def get_view(self):
        return self.v

    @staticmethod
    def get_unique_image_id():
        return None

    @staticmethod
    def get_device_id():
        return Nysa.get_id_from_name("LCD")

    @staticmethod
    def get_device_sub_id():
        return 3

    @staticmethod
    def get_device_unique_id():
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
                dev_index = n.find_device(Nysa.get_id_from_name("LCD"))
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

