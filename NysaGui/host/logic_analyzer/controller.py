#! /usr/bin/python

# Copyright (c) 2015 name (dave.mccoy@cospandesign.com)

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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qt import *

from nysa.common import status
from nysa.host import platform_scanner

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))

from nysa_base_controller import NysaBaseController
from view.view import View
from logic_analyzer_actions import LogicAnalyzerActions


sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             "common"))


# Put your device name (GPIO, SPI, I2C, etc...)
from nysa.host.driver.logic_analyzer import *

DRIVER = LogicAnalyzer
APP_NAME = "Logic Analyzer"

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

    @staticmethod
    def get_name():
        return APP_NAME

    @staticmethod
    def get_driver():
        return DRIVER

    def __init__(self):
        super (Controller, self).__init__()
        self.actions = LogicAnalyzerActions()
        self.actions.trigger_en_changed.connect(self.trigger_enable_changed)
        self.actions.trigger_pol_changed.connect(self.trigger_pol_changed)
        self.actions.enable_capture.connect(self.enable_capture)
        self.actions.reset_logic_analyzer.connect(self.reset_logic_analyzer)
        self.actions.repeat_count_changed.connect(self.repeat_count_changed)
        self.actions.trigger_offset_changed.connect(self.capture_offset_changed)
        self.actions.repeat_count_update.connect(self.update_repeat_count)
        self.actions.trigger_offset_update.connect(self.update_capture_offset)
        self.actions.restart_logic_analyzer.connect(self.restart_logic_analyzer)
        self.actions.capture_detected.connect(self.capture_detected)

    def _initialize(self, platform, urn):
        self.v = View(self.status, self.actions)
        self.v.setup_view()
        self.lax = LogicAnalyzer(platform, urn, debug = False)
        self.lax.set_both_edge(0x00000000)
        self.lax.set_trigger_edge(0xFFFFFFFF)
        self.v.update_enable(self.lax.is_enabled())
        if self.lax.is_enabled():
            self.lax.enable_interrupts(True)
        else:
            self.lax.enable_interrupts(False)

        self.v.update_repeat_count(self.lax.get_repeat_count())
        self.v.update_trigger_offset(self.lax.get_trigger_after())
        self.v.update_trigger_enable(self.lax.get_trigger_mask())
        self.v.update_trigger_polarity(self.lax.get_trigger())
        self.lax.register_interrupt_callback(self.actions.capture_detected)

    def start_tab_view(self, platform, urn, status):
        self.status = status
        self.status.Verbose( "Starting Template Application")
        self._initialize(platform, urn)

    def get_view(self):
        return self.v

    def capture_detected(self):
        print "Capture Detected"
        filepath = self.v.get_save_filepath()
        data = self.lax.read_data()
        clock_count = self.lax.get_clock_divider()
        buf = create_vcd_buffer(data, count = 32, clock_count = clock_count, add_clock = True)
        f = open(filepath, "w")
        f.write(buf)
        f.close()
        print "Wrote file: %s" % filename

    def trigger_enable_changed(self):
        value = self.v.get_trigger_enable()
        print "Trigger enable value: 0x%08X" % value
        self.lax.set_trigger_mask(value)

    def trigger_pol_changed(self):
        value = self.v.get_trigger_polarity()
        print "Trigger polarity value: 0x%08X" % value
        self.lax.set_trigger(value)

    def enable_capture(self, enable):
        if enable:
            print "Enable Capture!"
            if not self.lax.is_interrupts_enabled():
                self.lax.enable_interrupts(True)
        else:
            print "Disable Capture"
            if self.lax.is_interrupts_enabled():
                self.lax.enable_interrupts(False)

        self.lax.enable(enable)

    def reset_logic_analyzer(self):
        print "Reset Logic Analyzer"
        self.lax.reset()
        self.v.update_enable(self.lax.is_enabled())
        self.lax.enable_interrupts(False)
        self.update_repeat_count()
        self.update_capture_offset()
        self.update_trigger_polarity()
        self.update_trigger_enable()

    def restart_logic_analyzer(self):
        print "Restart Logic Analyzer"
        self.lax.restart()
        self.v.update_enable(self.lax.is_enabled())
        self.lax.enable_interrupts(False)
        self.update_repeat_count()
        self.update_capture_offset()
        self.update_trigger_polarity()
        self.update_trigger_enable()

    def repeat_count_changed(self):
        count = self.v.get_repeat_count()
        print "Repeat Count: %d" % count
        self.lax.set_repeat_count(count)

    def capture_offset_changed(self):
        offset = self.v.get_trigger_offset()
        print "Capture offset: %d" % offset
        self.lax.set_trigger_after(offset)

    def update_trigger_enable(self):
        self.v.update_trigger_enable(self.lax.get_trigger_mask())

    def update_trigger_polarity(self):
        self.v.update_trigger_polarity(self.lax.get_trigger())

    def update_repeat_count(self):
        print "Update the repeat count"
        repeat_count = self.lax.get_repeat_count()
        self.v.update_repeat_count(repeat_count)

    def update_capture_offset(self):
        print "Update capture offset"
        trigger_after = self.lax.get_trigger_after()
        self.v.update_trigger_offset(trigger_after)

    

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

