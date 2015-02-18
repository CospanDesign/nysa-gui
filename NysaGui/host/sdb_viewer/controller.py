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
SDB (Self Defined Bus Viewer)
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import argparse

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qt import *

from nysa.common import status
from nysa.host import platform_scanner
from nysa.host.driver.sdb import SDB
from nysa.cbuilder.sdb_component import convert_rom_to_32bit_buffer
from nysa.cbuilder.sdb_component import SDB_INTERCONNECT_MAGIC

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))

SDB_DESC_LOC = os.path.join(os.path.dirname(__file__),
                            os.pardir,
                            os.pardir,
                            "docs",
                            "sdb.txt")
from nysa_base_controller import NysaBaseController
from view.view import View

DRIVER = SDB
APP_NAME = "Self Defined Bus Viewer"

#Module Defines
n = str(os.path.split(__file__)[1])

DESCRIPTION = "\n" \
"\n"\
"%s\n" % APP_NAME

EPILOG = "\n"

class Controller(NysaBaseController):

    @staticmethod
    def get_name():
        return APP_NAME

    @staticmethod
    def get_driver():
        return DRIVER

    def __init__(self):
        super (Controller, self).__init__()
        f = open(SDB_DESC_LOC, 'r')
        s = f.read()
        f.close()
        s = s.split("DESCRIPTION START")[1]
        s = s.split("DESCRIPTION END")[0]
        self.sdb_desc = s

    def _initialize(self, platform, urn):
        self.platform = platform
        print "platform: %s" % str(self.platform)
        self.sdb_urn = urn
        self.v = View(self.status, self.actions)
        self.v.append_text(self.sdb_desc)
        #self.v.resize_columns()
        #self.v.collapse_all()
        self.setup_som_raw()
        self.setup_som_parsed()

    def start_tab_view(self, platform, urn, status):
        self.status = status
        self._initialize(platform, urn)

    def get_view(self):
        return self.v

    def setup_som_raw(self):
        self.sdb_rom = convert_rom_to_32bit_buffer(self.platform.read_sdb())
        rom = self.sdb_rom.splitlines()
        #print "rom: %s" % rom
        data = []
        component_data = None
        name = None
        address = "0x%04X" % 0x00
        buf = []
        for i in range (0, len(rom), 4):

            if (i % 16 == 0):
                if name is not None:
                    data.append([address, name, buf])
                    address = "0x%04X" % (i / 2)
                buf = []
                #print "rom data: %s" % str(rom[i])
                magic = "0x%s" % (rom[i].lower())
                last_val = int(rom[i + 15], 16) & 0xFF
                #print "magic: %s" % magic
                magic = int(rom[i], 16)
                #if (magic == hex(SDB_INTERCONNECT_MAGIC) and (last_val == 0)):
                if (magic == SDB_INTERCONNECT_MAGIC and (last_val == 0)):
                    name = "Interconnect"
                elif last_val == 0x01:
                    name = "Device"
                elif last_val == 0x02:
                    name = "Bridge"
                elif last_val == 0x80:
                    name = "Integration"
                elif last_val == 0x81:
                    name = "URL"
                elif last_val == 0x82:
                    name = "Synthesis"
                elif last_val == 0xFF:
                    name = "Empty"
                else:
                    name = "???"

            buf.append("%s %s : %s %s" % (rom[i], rom[i + 1], rom[i + 2], rom[i + 3]))
        data.append([address, name, buf])
        #print "sdb: %s" % str(data)
        for raw_sdb_component in data:
            self.v.add_sdb_raw_entry(data.index(raw_sdb_component), raw_sdb_component[0], raw_sdb_component[1], raw_sdb_component[2])

    def setup_som_parsed(self):
        self.v.set_sdb_parsed_som(self.platform.nsm.som)

def print_sdb(rom):
    rom = rom.splitlines()
    print "ROM"
    for i in range (0, len(rom), 4):
        if (i % 16 == 0):
            magic = "0x%s" % (rom[i].lower())
            last_val = int(rom[i + 15], 16) & 0xFF
            print ""
            if (magic == hex(SDB_INTERCONNECT_MAGIC) and last_val == 0):
                print "Interconnect"
            elif last_val == 0x01:
                print "Device"
            elif last_val == 0x02:
                print "Bridge"
            elif last_val == 0x80:
                print "Integration"
            elif last_val == 0x81:
                print "URL"
            elif last_val == 0x82:
                print "Synthesis"
            elif last_val == 0xFF:
                print "Empty"
            else:
                print "???"

        print "%s %s : %s %s" % (rom[i], rom[i + 1], rom[i + 2], rom[i + 3])

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

