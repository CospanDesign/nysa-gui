#! /usr/bin/python

# Copyright (c) 2014 name (email@example.com)

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

from nysa.common import status
from nysa.host import platform_scanner

from nysa.host.driver.sf_camera import SFCamera

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))


from nysa_base_controller import NysaBaseController

from sf_camera_actions import SFCameraActions
from view.camera_widget import CameraWidget

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             "common"))

#from protocol_utils.sf_camera.camera_utils import CameraUtils

import camera_engine
DRIVER = SFCamera
APP_NAME = "Sparkfun Camera Controller"



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

SF_CAMERA_IMAGE_ID = 260


class Controller(NysaBaseController):

    @staticmethod
    def get_name():
        return APP_NAME

    @staticmethod
    def get_driver():
        return DRIVER

    def __init__(self):
        super (Controller, self).__init__()
        self.actions = SFCameraActions()
        self.debug = False
        self.actions.sf_camera_run.connect(self.run)
        self.actions.sf_camera_reset.connect(self.reset)
        self.actions.sf_camera_stop.connect(self.stop)

    def __del__(self):
        pass
        #self.camera_util.stop()

    def _initialize(self, platform, urn):
        self.v = CameraWidget(self.status, self.actions)

        self.camera = SFCamera(platform, urn)
        self.engine = camera_engine.CameraEngine(self.camera, self.actions, self.status)

    def start_tab_view(self, platform, urn, status):
        self.status = status
        self.status.Verbose("Starting Sparkfun Video")
        self._initialize(platform, urn)

    def get_view(self):
        return self.v

    def run(self):
        self.status.Important("Start")
        #self.status.Important( "Initiate new thread")
        #self.camera_util.run()
        self.engine.start()

    def stop(self):
        self.status.Important("Stop")
        #self.status.Important( "Stop Reading")
        #self.camera_util.stop()
        self.engine.stop()

    def reset(self):
        self.status.Important("Reset")
        #self.status.Important( "Reset Camera")
        #self.camera_util.reset()
        self.engine.reset()

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

