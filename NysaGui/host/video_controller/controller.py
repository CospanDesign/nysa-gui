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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qt import *

from nysa.common import status
from nysa.host import platform_scanner

from nysa.host.driver.lcd_SSD1963 import LCDSSD1963
#from nysa.host.driver.lcd_ST7781R import LCDST7781R

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

DRIVER = LCDSSD1963
APP_NAME = "Video Playback"

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

    def __init__(self):
        super (Controller, self).__init__()
        self.actions = VideoActions()
        self.actions.color_test.connect(self.color_test)

    def _initialize(self, platform, urn):
        self.v = View(self.actions, self.status)
        self.lcd = LCDSSD1963(platform, urn, debug = False)
        self.platform_name = platform.get_board_name()

        if self.platform_name == "sim":
            return

        self.lcd.setup()
        self.v.set_lcd(self.lcd)

    def color_test(self):
        if self.platform_name == "sim":
            self.status.Important("Cannot test color test on sim platform")
            return
            
        width = self.lcd.get_image_width()
        height = self.lcd.get_image_height()
        #width = 480
        #height = 272
        #size = width * height * 2
        size = width * height
        print "Image Width: %d" % width
        print "Image Height: %d" % height
        print "Total Size: %d" % size
        print "Total Size: 0x%08X" % size
        #Write a color to memory
        red    = 0xFF000000
        green  = 0x00FF0000
        blue   = 0x0000FF00
        cyan   = 0x00FFF000
        purple = 0xF000FF00
        orange = 0xFFF00000
        pink   = 0xFF707000
        white  = 0xFFFFFFFF

        #color = white
        color = 0x00000000
        image0 = Array('B')
        for i in range(size):
            if (i % 480) == 0:
                if (i / 480 / 256) > 0:
                    color = 0
                else: 
                    color += 0x000100 << 8
            image0.append((color >> 24) & 0xFF)
            image0.append((color >> 16) & 0xFF)
            image0.append((color >> 8) & 0xFF)
            image0.append(color & 0xFF)


        color = pink
        image1 = Array('B')
        for i in range(size):
            image1.append((color >> 24) & 0xFF)
            image1.append((color >> 16) & 0xFF)
            image1.append((color >> 8) & 0xFF)
            image1.append(color & 0xFF)

        color = purple
        image2 = Array('B')
        for i in range(size):
            image2.append((color >> 24) & 0xFF)
            image2.append((color >> 16) & 0xFF)
            image2.append((color >> 8) & 0xFF)
            image2.append(color & 0xFF)
        
        color = red
        image3 = Array('B')
        for i in range(size):
            image3.append((color >> 24) & 0xFF)
            image3.append((color >> 16) & 0xFF)
            image3.append((color >> 8) & 0xFF)
            image3.append(color & 0xFF)


        color = orange
        image4 = Array('B')
        for i in range(size):
            image4.append((color >> 24) & 0xFF)
            image4.append((color >> 16) & 0xFF)
            image4.append((color >> 8) & 0xFF)
            image4.append(color & 0xFF)

        print "Writing first image..."
        self.lcd.dma_writer.write(image0)
        '''
        #print "Wrote first image"
        self.lcd.dma_writer.write(image1)
        #print "Wrote second image"
        self.lcd.dma_writer.write(image2)
        #print "Wrote third image"
        self.lcd.dma_writer.write(image3)
        #print "Wrote forth image"
        self.lcd.dma_writer.write(image4)
        '''

    def start_standalone_app(self, platform, urn, status, debug = False):
        app = QApplication (sys.argv)
        main = QtGui.QMainWindow()

        self.status = status.Status()
        if debug:
            self.status.set_level(status.StatusLevel.VERBOSE)
        else:
            self.status.set_level(status.StatusLevel.INFO)
        self.status.Verbose("Starting Standalone Application")
        self._initialize(platform, urn)
        main.setCentralWidget(self.v)
        main.show()
        sys.exit(app.exec_())

    def start_tab_view(self, platform, urn, status):
        self.status = status
        self.status.Verbose("Starting Video Application")
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

