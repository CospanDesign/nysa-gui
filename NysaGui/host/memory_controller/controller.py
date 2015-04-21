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
memory controller
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import argparse
import time
from array import array as Array

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qt import *

from nysa.common import status
from nysa.host import platform_scanner
from nysa.host.driver.memory import Memory

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))

from nysa_base_controller import NysaBaseController
from view.view import View

from memory_actions import MemoryActions

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))

# Put your device name (GPIO, SPI, I2C, etc...)
DRIVER = Memory
APP_NAME = "Memory Controller"

#Module Defines
n = str(os.path.split(__file__)[1])

DESCRIPTION = "\n" \
"\n"\
"Memory Controller\n"

EPILOG = "\n" \
"\n"\
"Examples:\n"\
"\tSomething\n" \
"\t\t%s Something\n"\
"\n" % n

MAX_LONG_SIZE = 0x0800000
#MAX_LONG_SIZE = 0x0200000

class ReaderThread(QThread):
    def __init__(self, mutex, func):
        super(ReaderThread, self).__init__()

        self.memory_actions = MemoryActions()
        self.mutex = mutex
        self.func = func

    def run(self):
        #Perform Memory Test
        self.mutex.lock()
        result = "Error"
        result = self.func()
        self.mutex.unlock()
        self.memory_actions.memory_read_finished.emit(result)

class Controller(NysaBaseController):

    @staticmethod
    def get_name():
        return APP_NAME

    @staticmethod
    def get_driver():
        return DRIVER

    def __init__(self):
        super (Controller, self).__init__()
        self.status = None
        self.actions = None
        self.memory_actions = MemoryActions()
        self.mutex = QMutex()
        self.reader_thread = None
        self.memory_actions.memory_test_start.connect(self.start_tests)
        self.memory_actions.memory_read_finished.connect(self.run_test)

    def __del__(self):
        if self.reader_thread is not None:

            self.status.Important( "Waiting for reader thread to finish")
            self.reader_thread.join()

    def _initialize(self, platform, urn):
        self.n = platform
        self.urn = urn
        self.v = View(self.status, self.memory_actions)
        self.v.setup_view()
        self.v.add_test("Single Read/Write at Start", True, self.test_single_rw_start)
        self.v.add_test("Single Read/Write at End", True, self.test_single_rw_end)
        self.v.add_test("Long Read/Write Test", True, self.test_long_burst)
        self.v.set_memory_size(self.n.get_device_size(urn))
        self.v.set_memory_offset(self.n.get_device_address(urn))

    def start_tab_view(self, platform, urn, status):
        self.status = status
        self._initialize(platform, urn)

    def get_view(self):
        return self.v

    def start_tests(self):
        print "Start Tests!"
        self.gen = test_iterator(self.v.get_num_tests())
        self.run_test()

    def get_test(self):
        index = self.gen.next()
        if self.v.is_test_enabled(index):
            return self.v.get_test_function(index)
        return None

    def run_test(self, status = None):
        finished = False
        if status is not None:
            print "Finished test, Result: %s" % status
        try:
            while not finished:
                t = self.get_test()
                if t is not None:
                    print "Running Test: %s" % str(t)
                    self.reader_thread = ReaderThread(self.mutex, t)
                    self.reader_thread.start()
                    return
                else:
                    continue
        except StopIteration:
            print "Done!"

    def test_single_rw_start(self):
        status = "Passed"
        print "device URN: %s" % self.urn
        size = self.n.get_device_size(self.urn)
        offset = self.n.get_device_address(self.urn)
        print "size: 0x%08X" % size
        print "offset: 0x%08X" % offset
        self.clear_memory()
        if self.status.is_command_line():
            self.status.Verbose( "Test Single Read/Write at Beginning")
        data_out = Array('B', [0xAA, 0xBB, 0xCC, 0xDD, 0x55, 0x66, 0x77, 0x88])
        self.n.write_memory(offset, data_out)
        print "Wrote second part!"
        data_in = self.n.read_memory(offset, len(data_out)/4)
        print "length: data_out: %d, data_in: %d" % (len(data_out), len(data_in))
        print "data out: %s" % str(data_out)
        print "data_in: %s" % str(data_in)
        for i in range (len(data_out)):
            if data_in[i] != data_out[i]:
                status = "Failed"
                print "Error at: 0x%02X OUT: 0x%08X IN: 0x%08X" % (i, data_out[i], data_in[i])
                #print "ERROR at: [{0:>2}] OUT: {1:>8} IN: {2:>8}".format(str(i), hex(data_out[i]), hex(data_in[i]))
        return status

    def test_single_rw_end(self):
        status = "Passed"
        size = self.n.get_device_size(self.urn)
        offset = self.n.get_device_address(self.urn)
        self.clear_memory()

        if self.status.is_command_line():
            self.status.Verbose( "Test Single Read/Write at End")
        data_out = Array('B', [0xAA, 0xBB, 0xCC, 0xDD, 0x55, 0x66, 0x77, 0x88])
        self.n.write_memory(offset + (size - 16), data_out)
        print "Reading from location: 0x%08X" % (size - 16)
        data_in = self.n.read_memory(offset + (size - 16), 2)

        for i in range (len(data_out)):
            if data_in[i] != data_out[i]:
                print "Error at: 0x%02X OUT: 0x%08X IN: 0x%08X" % (i, data_out[i], data_in[i])
                #print "ERROR at: [{0:>2}] OUT: {1:>8} IN: {2:>8}".format(str(i), hex(data_out[i]), hex(data_in[i]))
                status = "Failed"

        return status

    def test_long_burst(self):
        status = "Passed"
        fail = False
        fail_count = 0
        position = 0
        self.clear_memory()
        total_size = self.n.get_device_size(self.urn)
        offset = self.n.get_device_address(self.urn)

        size = 0
        if total_size > MAX_LONG_SIZE:
            self.status.Info("Memory Size: 0x%08X is larger than read/write size" % total_size)
            self.status.Info("\tBreaking transaction into 0x%08X chunks" % MAX_LONG_SIZE)
            size = MAX_LONG_SIZE
        else:
            size = total_size

        #Write Data Out
        while position < total_size:
            data_out = Array('B')

            if self.status.is_command_line():
                self.status.Verbose( "long rw")
            data_out = Array('B')
            for i in range (0, size):
                data_out.append((i % 255))

            if self.status.is_command_line():
                self.status.Verbose( "Writing 0x%08X bytes of data" % (len(data_out)))
            start = time.time()
            self.n.write_memory(offset + position, data_out)
            end = time.time()
            if self.status.is_command_line():
                self.status.Verbose( "Write Time : %f" % (end - start))
                self.status.Verbose( "Reading 0x%08X bytes of data" % (len(data_out)))

            #Increment the position
            prev_pos = position
            position += size

            if position + size > total_size:
                size = total_size - position

            if self.status:
                self.status.Info("Wrote: 0x%08X - 0x%08X" % (prev_pos, position))


        position = 0

        start = time.time()
        if total_size > MAX_LONG_SIZE:
            self.status.Info("Memory Size: 0x%08X is larger than read/write size" % total_size)
            self.status.Info("\tBreaking transaction into 0x%08X chunks" % MAX_LONG_SIZE)

            size = MAX_LONG_SIZE
        else:
            size = total_size
 
        while position < total_size:

            data_in = self.n.read_memory(offset + position, len(data_out) / 4)
            end = time.time()
            if self.status.is_command_line():
                self.status.Verbose( "Read Time: %f" % (end - start))
                self.status.Verbose( "Comparing Values")
            if len(data_out) != len(data_in):
                if self.status.is_command_line():
                    self.status.Error( "Data in lenght not equal to data_out length")
                    self.status.Error( "\toutgoing: %d" % len(data_out))
                    self.status.Error( "\tincomming: %d" % len(data_in))

            dout = data_out.tolist()
            din = data_in.tolist()

            for i in range(len(data_out)):
                out_val = dout[i]
                in_val = din[i]
                if out_val != in_val:
                    fail = True
                    status = "Failed"
                    self.status.Error("%d and %d not equal" % (out_val, in_val))
                    self.status.Error("Mismatch @ 0x%08X: Write: (Hex): 0x%08X Read (Hex): 0x%08X" % (i, data_out[i], data_in[i]))
                    if fail_count >= 16:
                        break
                    fail_count += 1

            prev_pos = position
            position += size
            if position + size > total_size:
                size = total_size - position

            if self.status:
                self.status.Info("Read: 0x%08X - 0x%08X" % (prev_pos, position))

        return status

    def clear_memory(self):
        total_size = self.n.get_device_size(self.urn)
        offset = self.n.get_device_address(self.urn)
        position = 0
        size = 0
        if self.status.is_command_line():
            self.status.Verbose( "Clearing Memory")
            self.status.Verbose( "Memory Size: 0x%08X" % size)

        if total_size > MAX_LONG_SIZE:
            self.status.Info("Memory Size: 0x%08X is larger than read/write size" % total_size)
            self.status.Info("\tBreaking transaction into 0x%08X chunks" % MAX_LONG_SIZE)
            size = MAX_LONG_SIZE
        else:
            size = total_size

        while position < total_size:
            data_out = Array('B')
            for i in range(0, ((size / 4) - 1)):
                num = 0x00
                data_out.append(num)

            self.n.write_memory(offset + position, data_out)

            #Increment the position
            prev_pos = position
            position += size

            if position + size > total_size:
                size = total_size - position

            if self.status:
                self.status.Verbose("Cleared: 0x%08X - 0x%08X" % (prev_pos, position))

def test_iterator(count):
    index = 0
    while index < count:
        yield index
        index += 1

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

