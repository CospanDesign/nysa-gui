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
I2C Controller
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import argparse

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qt import *

from nysa.host import platform_scanner

#I2C Driver
from nysa.host.driver.i2c import I2C


sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))

from nysa_base_controller import NysaBaseController

#I2C Protocol Utility
from view.i2c_widget import I2CWidget

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             "common"))


from protocol_utils.i2c.i2c_controller import I2CController
from protocol_utils.i2c.i2c_engine import I2CEngine
from protocol_utils.i2c.i2c_engine import I2CEngineError

import status

# Put your device name (GPIO, SPI, I2C, etc...)
DRIVER = I2C
APP_NAME = "I2C Controller"

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

from i2c_actions import I2CActions

from NysaGui.common.udp_server import UDPServer
I2C_PORT = 0xC594

class Controller(NysaBaseController):

    def __init__(self):
        super (Controller, self).__init__()
        self.actions = I2CActions()
        self.i2c = None
    
    def __del__(self):
        if self.i2c is not None:
            self.i2c.enable_i2c(False)

    def _initialize(self, platform, urn):
        self.i2c = I2C(platform, urn, status)
        self.m = I2CController(self.status, self.actions)
        self.server = UDPServer(self.status, self.actions, I2C_PORT)

        self.engine = I2CEngine(self.i2c, self.status, self.actions, self.server)
        init_transactions = self.m.get_all_init_transactions()
        #print "Transactions: %s" % str(test)
        self.v = I2CWidget(self.status, self.actions)
        self.v.update_i2c_init_transactions(init_transactions)
        self.v.set_save_callback(self.save_callback)
        self.v.set_load_callback(self.load_callback)
        self.v.set_load_default_callback(self.load_default_callback)
        #print "Files: %s" % str(files)
        self.v.load_default_scripts()

        self.actions.i2c_run.connect(self.i2c_run)
        self.actions.i2c_step.connect(self.i2c_step)
        self.actions.i2c_loop_step.connect(self.i2c_loop_step)

    def start_tab_view(self, platform, urn, status):
        self.status = status
        self.status.Verbose( "Starting I2C Application")
        self._initialize(platform, urn)

    def get_view(self):
        return self.v

    def i2c_run(self):
        init_transactions = self.m.get_all_init_transactions()
        loop_transactions = self.m.get_all_loop_transactions()

        if not self.engine.is_running():
            self.engine.start_engine(init_transactions, loop_transactions)
        else:
            self.engine.load_commands(init_transactions, loop_transactions)

    def i2c_step(self):
        init_transactions = self.m.get_all_init_transactions()
        loop_transactions = self.m.get_all_loop_transactions()

        if not self.engine.is_running():
            self.engine.start_engine(init_transactions, loop_transactions, pause = True)

        self.engine.pause_flow()
        self.engine.step_flow()

    def i2c_loop_step(self):
        init_transactions = self.m.get_all_init_transactions()
        loop_transactions = self.m.get_all_loop_transactions()

        if not self.engine.is_running():
            self.engine.start_engine(init_transactions, loop_transactions, pause = True)

        self.engine.pause_flow()
        self.engine.step_loop_flow()

    def save_callback(self):
        filename = self.v.get_filename()
        name = self.v.get_config_name()
        description = self.v.get_config_description()
        self.status.Important( "Saving I2C Config File: %s" % filename)
        self.m.save_i2c_commands(filename, name, description)
        
    def load_default_callback(self, filename):
        self.status.Important( "Loading Default I2C Config File: %s" % filename)
        self.m.load_i2c_commands(filename)
        self.v.set_config_name(self.m.get_config_name())
        self.v.set_config_description(self.m.get_config_description())

    def load_callback(self):
        filename = self.v.get_filename()
        self.status.Important( "Loading I2C Config File: %s" % filename)
        self.m.load_i2c_commands(filename)

        self.v.set_config_name(self.m.get_config_name())
        self.v.set_config_description(self.m.get_config_description())

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

