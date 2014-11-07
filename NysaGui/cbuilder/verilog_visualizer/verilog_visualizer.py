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


import argparse
import sys
import os

from PyQt4.Qt import *
from PyQt4.QtCore import *

p = os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir)

sys.path.append(p)

from actions import Actions
from view.main_view import MainForm


DESCRIPTION = "\n" \
"\n"\
"usage: verilog_visualizer.py [options]\n"

EPILOG = "\n" \
"\n"\
"Examples:\n"\
"\tSomething\n" \
"\t\ttest_dionysus.py\n"\
"\n"

debug = False

class VerilogVisualizerGUI(QObject):

    def __init__(self):
        super (VerilogVisualizerGUI, self).__init__()
        app = QApplication(sys.argv)
        self.actions = Actions()
        QThread.currentThread().setObjectName("Verilog Visualizer GUI")
        self.view = MainForm(self.actions)

        sys.exit(app.exec_())

def main(argv):
    #Parse out the commandline arguments
    parser = argparse.ArgumentParser(
            formatter_class = argparse.RawDescriptionHelpFormatter,
            description = DESCRIPTION,
            epilog = EPILOG
    )
    debug = False

    parser.add_argument("-d", "--debug",
                        action = "store_true",
                        help = "Enable Debug Messages")

    args = parser.parse_args()

    if args.debug:
        print ("Debug Enable")
        debug = True

    n = VerilogVisualizerGUI()

if __name__ == "__main__":
    main(sys.argv)

