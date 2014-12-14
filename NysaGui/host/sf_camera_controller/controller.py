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

from PyQt4.Qt import QApplication
from PyQt4 import QtCore

#Platform Scanner
from nysa.host.platform_scanner import PlatformScanner
from nysa.host.driver.sf_camera import SFCamera

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))


from nysa_base_controller import NysaBaseController
from nysa.common import status

from sf_camera_actions import SFCameraActions
from view.camera_widget import CameraWidget
from model.model import AppModel


sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             "common"))

#from protocol_utils.sf_camera.camera_utils import CameraUtils

import camera_engine


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

SF_CAMERA_IMAGE_ID = 260


class Controller(NysaBaseController):

    def __init__(self):
        super (Controller, self).__init__()
        self.actions = SFCameraActions()
        self.m = AppModel()
        self.debug = False
        self.actions.sf_camera_run.connect(self.run)
        self.actions.sf_camera_reset.connect(self.reset)
        self.actions.sf_camera_stop.connect(self.stop)

    def __del__(self):
        pass
        #self.camera_util.stop()

    @staticmethod
    def get_name():
        #Change this for your app
        return "Sparkfun 640x480 Camera Controller"

    def _initialize(self, platform):
        self.v = CameraWidget(self.status, self.actions)
        self.camera = SFCamera(platform[2], camera_id = 0, i2c_id = 1)
        #self.camera_util = CameraUtils(self.camera, self.actions, self.status)
        self.engine = camera_engine.CameraEngine(self.camera, self.actions, self.status)
        #self.camera_util.setup_camera()

    def start_standalone_app(self, platform, debug = False):
        app = QApplication (sys.argv)
        self.status = status.Status()
        self._initialize(platform)
        sys.exit(app.exec_())

    def start_tab_view(self, platform, status):
        self.status = status
        self.status.Verbose("Starting Sparkfun Video")
        self._initialize(platform)

    def get_view(self):
        return self.v

    @staticmethod
    def get_unique_image_id():
        """
        Unique Image ID for SF Camera can be found in the configuration file

        '/nysa/ibuilder/example_projects/dionysus_sf_camera.json'

        """
        return SF_CAMERA_IMAGE_ID

    @staticmethod
    def get_device_id():
        return None

    @staticmethod
    def get_device_sub_id():
        return None

    @staticmethod
    def get_device_unique_id():
        return None

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
    plat = None

    if args.debug:
        s.set_level(status.StatusLevel.VERBOSE)
        s.Debug(None, "Debug Enabled")
        debug = True

    pscanner = PlatformScanner()
    ps = pscanner.get_platforms()
    image_id = None
    for p in ps:
        s.Verbose(p)
        for psi in ps[p]:
            if plat is None:
                s.Verbose("Found a platform: %s" % p)
                n = ps[p][psi]
                n.read_drt()
                #n.drt_manager.pretty_print_drt()
                image_id = n.get_image_id()
                #print "image id: %s" % str(image_id)
                if image_id is not None and image_id == SF_CAMERA_IMAGE_ID:
                    print "Found an image ID that matches: %d" % image_id
                    plat = [p, psi, ps[p][psi]]
                    break

            s.Verbose("\t%s" % psi)

    if args.list:
        s.Verbose("Listed all platforms, exiting")
        sys.exit(0)

    if plat is not None:
        s.Important("Using: %s" % plat)
    else:
        s.Fatal("Didn't find a platform to use!")

    c = Controller()
    c.start_standalone_app(plat, debug)

if __name__ == "__main__":
    main(sys.argv)
