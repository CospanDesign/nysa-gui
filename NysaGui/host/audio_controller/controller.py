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
Audio Playback controller
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import wave
import struct
import argparse
import time
from Queue import Queue

from array import array as Array

from PyQt4.Qt import QApplication
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qt import *

from nysa.common import status
from nysa.host.nysa import Nysa
from nysa.host import platform_scanner
from nysa.host.driver.i2s import I2S


sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

#Platform Scanner
sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))

from common import status as sts 

from nysa_base_controller import NysaBaseController
from view.view import View

from audio_actions import AudioActions


from nysa.common import site_manager
from nysa.host import platform_scanner
from nysa.host.platform_scanner import PlatformScanner

DRIVER = I2S
APP_NAME = "Audio Playback"
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

    @staticmethod
    def get_name():
        return APP_NAME

    @staticmethod
    def get_driver():
        return DRIVER

    def __init__(self):
        super (Controller, self).__init__()
        self.actions = AudioActions()
        self.thread = QThread()
        self.thread.start()
        self.audio_worker = AudioWorker()
        self.audio_worker.moveToThread(self.thread)
        self.actions.play_audio.connect(self.play_audio)
        self.actions.pause_audio.connect(self.pause_audio)
        self.actions.stop_audio.connect(self.stop_audio)
        self.actions.play_1khz.connect(self.play_1khz)

        self.filename = ""

    def _initialize(self, platform, urn):
        self.v = View(self.actions, self.status)
        self.platform_name = platform.get_board_name()
        self.status.Verbose("Platform Name: %s" % self.platform_name)
        self.i2s = I2S(platform, urn, debug = False)
        QMetaObject.invokeMethod(self.audio_worker,
                                 "thread_init",
                                 Qt.QueuedConnection,
                                 Q_ARG(object, self),
                                 Q_ARG(object, self.status),
                                 Q_ARG(object, self.i2s),
                                 Q_ARG(object, self.actions))

        self.actions.set_audio_file.connect(self.set_audio_file)
        self.i2s.enable_i2s(True)
        self.i2s.enable_interrupt(True)
        self.set_audio_file("/home/cospan/sandbox/wave_file.wav")

    def start_tab_view(self, platform, urn, status):
        self.status = status
        self.status.Verbose("Starting Audio Application")
        self._initialize(platform, urn)

    def get_view(self):
        return self.v

    #Audio Controller
    def set_audio_file(self, filename):
        self.filename = filename
        self.status.Important("set filename: %s" % self.filename)
        self.v.set_audio_filename(filename)
        QMetaObject.invokeMethod(self.audio_worker,
                                 "set_audio_filename",
                                 Qt.QueuedConnection,
                                 Q_ARG(object, self.filename))

    def play_audio(self):
        #self.audio_worker.play_audio()
        print "play audio!"
        QMetaObject.invokeMethod(self.audio_worker,
                                 "play_audio",
                                 Qt.QueuedConnection)

    def pause_audio(self):
        QMetaObject.invokeMethod(self.audio_worker,
                                 "pause_audio",
                                 Qt.QueuedConnection)

    def stop_audio(self):
        QMetaObject.invokeMethod(self.audio_worker,
                                 "stop_audio",
                                 Qt.QueuedConnection)

    def play_1khz(self):
        if self.i2s.is_post_fifo_test_enabled():
            self.i2s.enable_post_fifo_test(False)
        else:
            self.i2s.enable_post_fifo_test(True)

    def set_audio_position(self, position):
        print "set audio position: %f" % position
        QMetaObject.invokeMethod(self.audio_worker,
                                 "stop_audio",
                                 Qt.QueuedConnection,
                                 Q_ARG(position))

    @pyqtSlot(float)
    def update_audio(self, position):
        print "Updating audio"
        self.v.update_audio_position(position)

class AudioProcessor(QObject):
    def __init__(self, audio_worker, status, i2s, queue, actions):
        super(AudioProcessor, self).__init__()
        self.audio_worker = audio_worker
        self.status = status
        self.queue = queue
        self.actions = actions
        self.i2s = i2s

    @pyqtSlot(object)
    def initiate_process(self, filename):
        self.filename = filename
        try:
            wf = wave.open(filename, 'rb')
        except wave.Error as err:
            self.status.Error("Unable to open Wave File: %s" % str(err))
            return
        self.status.Info("Opened file: %s" % filename)

        self.status.Debug("Number of channels: %d" % wf.getnchannels())
        self.status.Debug("Sample Width: %d" % wf.getsampwidth())
        self.status.Debug("Get frame rate: %d" % wf.getframerate())
        self.status.Debug("Number of Frames: %d" % wf.getnframes())
        self.status.Debug("Type of compression: %s" % wf.getcomptype())

        self.status.Verbose("Getting raw data")
        audio_data = wf.readframes(wf.getnframes())
        self.status.Verbose("Got raw data")
        total_samples = wf.getnframes() * wf.getnchannels()
        sample_width = wf.getsampwidth()

        divisor = 8
        #divisor = 100
        self.i2s.set_clock_divisor(divisor)
        self.status.Verbose("Setting divisor: %d" % self.i2s.get_clock_divisor())
        wf.close()

        self.status.Verbose("Chunk size: 0x%08X" % self.i2s.get_mem_block_size())

        #Start processing data to be in chunks
        #thanks SaphireSun for this peice of code
        #http://stackoverflow.com/questions/2226853/interpreting-wav-data
        fmt = None
        if sample_width == 1:
            fmt = "%iB" % total_samples # read unsigned chars
        elif sample_width == 2:
            fmt = "%ih" % total_samples # Read signed 2 byte shorts
        else:
            self.status.Error("Only support 8 and 16 bit Audio File Formats!")
            return
        integer_data = struct.unpack(fmt, audio_data)
        del audio_data
        self.status.Debug("Got integer data")
        self.status.Debug("Start Processing Audio Data")
        chunk_size = self.i2s.get_mem_block_size() / 4


        chunk_pos = 0
        total_size = len(integer_data)

        total_chunk_count = int(total_size / chunk_size)
        if chunk_size % total_size != 0:
            total_chunk_count += 1
            
        self.actions.update_total_chunk_count.emit(total_chunk_count)

        audio_data = Array('B')
        if sample_width == 1:
            for i in range (total_size):
                value = (integer_data[i] & 0xFF) << 16
                audio_data.append((value >> 24) & 0xFF)
                audio_data.append((value >> 16) & 0xFF)
                audio_data.append((value >> 8) & 0xFF)
                audio_data.append(value & 0xFF)

                #Increment the position in the chunk
                chunk_pos += 1
                if chunk_pos >= chunk_size:
                    chunk_pos = 0
                    self.queue.put(audio_data)
                    pos = int(100 * (1.0 * i) / (1.0 * total_size))
                    self.actions.convert_audio_update.emit(pos)
                    #self.status.Debug("converted %d%%" % pos)
                    audio_data = Array('B')

        elif sample_width == 2:
            lr = False
            for i in range (total_size):
                value = 0x00000000
                if lr:
                    value = 0x80000000

                #change the value to a 24-bit audio sample
                value = value | ((integer_data[i] & 0xFFFF) << 8)

                audio_data.append((value >> 24) & 0xFF)
                audio_data.append((value >> 16) & 0xFF)
                audio_data.append((value >> 8) & 0xFF)
                audio_data.append(value & 0xFF)
                chunk_pos += 1
                if chunk_pos >= chunk_size:
                    chunk_pos = 0
                    self.queue.put(audio_data)
                    pos = int(100 * (1.0 * i) / (1.0 * total_size))
                    self.actions.convert_audio_update.emit(pos)
                    #self.status.Debug("converted %d%%" % pos)
                    self.status.Debug("Thread Name: %s" % self.thread().objectName())
                    #time.sleep(.1)
                    audio_data = Array('B')
                lr = not lr

        if chunk_pos > 0:
            self.queue.put(audio_data)
            self.status.Debug("Processed and sent chunk 100%")
        self.actions.convert_audio_update.emit(100)

#Audio Worker
class AudioWorker(QObject):
    def __init__(self):
        super(AudioWorker, self).__init__()

    @pyqtSlot(object, object, object, object)
    def thread_init(self, controller, status, i2s, actions):
        self.stop = False
        self.pause = False
        self.controller = controller
        self.status = status
        self.thread().setObjectName("Worker thread")
        self.audio_queue = Queue()
        self.audio_data = []
        self.status.Info("Intialize audio worker thread")
        self.i2s = i2s
        self.actions = actions
        self.processing_thread = QThread()
        self.processing_thread.setObjectName("Processor thread")
        self.processing_thread.start()
        self.audio_processor = AudioProcessor(self, self.status, i2s, self.audio_queue, actions)
        self.audio_processor.moveToThread(self.processing_thread)

        self.actions.update_total_chunk_count.connect(self.update_total_chunk_count)
        self.actions.convert_audio_update.connect(self.convert_audio_update)
        self.chunk_count = 0
        self.total_chunk_count = 0
        self.position = 0
        self.state = "stop"

    @pyqtSlot(object)
    def set_audio_filename(self, filename):
        QMetaObject.invokeMethod(self.audio_processor,
                                 "initiate_process",
                                 Qt.QueuedConnection,
                                 Q_ARG(object, filename))
        #self.i2s.enable_i2s(True)
        #self.i2s.enable_interrupt(True)

    def update_total_chunk_count(self, chunk_count):
        self.position = 0
        self.total_chunk_count = chunk_count
        self.status.Debug("Updated chunk count to: %d" % self.total_chunk_count)

    def convert_audio_update(self, pos):
        #audio_data = self.audio_queue.get()
        #self.status.Verbose("Adding chunk with length: 0x%08X" % len(audio_data))
        #self.status.Verbose("Adding chunk with length: 0x%08X" % len(self.audio_queue))
        self.status.Verbose("Adding chunk with length")
        #self.audio_data.append(audio_data)

    @pyqtSlot(object)
    def set_i2s(self, i2s):
        self.i2s = i2s

    @pyqtSlot()
    def stop_audio(self):
        self.chunk_count = 0
        self.stop = True
        self.audio_data = []

    def i2s_interrupt_callback(self):
        print "callback"
        if self.stop:
            return
        #QMetaObject.invokeMethod(self,
        #                         "play_audio",
        #                         Qt.QueuedConnection)

    @pyqtSlot()
    def pause_audio(self):
        self.pause = True

    @pyqtSlot(object)
    def set_position(self, pos):
        if self.total_chunk_count == 0:
            return
        self.position = int(pos * self.total_chunk_count)

    @pyqtSlot()
    def play_audio(self):
        print "playing audio!"
        self.status.Debug("Thread Name: %s" % self.thread().objectName())
        self.stop = False
        if self.total_chunk_count == 0:
            self.status.Error("No data to send")
            self.stop = True
            return

        if self.position >= self.total_chunk_count:
            self.status.Info("Finished playing music")
            self.stop = True
            return

        if self.pause:
            print "pause!"
            return

        '''
        if self.position > len(self.audio_data):
            self.status.Warning("Position requested is greater than avaialble data")
            p = int(100 * (1.0 * self.position) / (1.0 * self.total_chunk_count))
            t = int(100 * (1.0 * len(self.audio_data)) / (1.0 * self.total_chunk_count))

            if len(self.audio_data) == 0:
                self.status.Warning("There is no available audio data!")
            self.position = len(self.audio_data) - 1
            self.status.Warning("\t%d > %d")
            self.status.Warning("\tSetting position to the last block")
        '''

        while self.position < self.total_chunk_count:
            self.status.Debug("Writing Position: %d" % self.position)
            if self.stop:
                return
            #self.i2s.write_audio_data(self.audio_data[self.position])
            self.i2s.write_audio_data(self.audio_queue.get())
            #self.i2s.write_audio_data(self.audio_data)
            val = ((1.0 * self.position) / (1.0 * self.total_chunk_count))
            print "value: %f" % val
            self.controller.update_audio(val)
            self.position = self.position + 1

        '''
        mb = self.i2s.get_available_memory_blocks()
        if mb == 0:
            #No space available
            self.status.Debug("No space to send data")
            return
        elif mb == 0x01 or mb == 0x02:
            #one block is available
            self.i2s.write_audio_data(self.audio_data[self.position])
            self.position += 1
            #val = (100 * ((1.0 * self.position) / (1.0 * self.total_chunk_count)))
            val = ((1.0 * self.position) / (1.0 * self.total_chunk_count))
            self.controller.update_audio(val)
            #QMetaObject.invokeMethod(self.controller,
            #                         "update_audio",
            #                         Qt.QueuedConnection,
            #                         Q_ARG(float, val))
        else:
            self.i2s.write_audio_data(self.audio_data[self.position])
            self.position += 1
            val = ((1.0 * self.position) / (1.0 * self.total_chunk_count))
            self.controller.update_audio(val)
            #QMetaObject.invokeMethod(self.controller,
            #                         "update_audio",
            #                         Qt.QueuedConnection,
            #                         Q_ARG(float, val))

            self.i2s.write_audio_data(self.audio_data[self.position])
            self.position += 1
            val = ((1.0 * self.position) / (1.0 * self.total_chunk_count))
            self.controller.update_audio(val)
            #QMetaObject.invokeMethod(self.controller,
            #                         "update_audio",
            #                         Qt.QueuedConnection,
            #                         Q_ARG(float, val))
        '''

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

