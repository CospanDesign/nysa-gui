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
Video Controller
"""


__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import time
import json

from array import array as Array

from PyQt4 import QtCore
from PyQt4.QtCore import QObject

from PyQt4.QtCore import *
from PyQt4.QtGui import *

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.common import status as clstatus
from nysa.host.driver.lcd_SSD1963 import LCD


class VideoEngineError(Exception):
    pass


class VideoEngineWorker(QObject):

    def __init__(self):
        super (VideoEngineWork, self).__init__()

    @QtCore.pyqtSlot(object, object)
    def thread_init(self,
                    video,
                    actions)

        print "Initialize video thread"
        self.video = video
        self.actions = actions
        self.status = clstatus.Status()
        self.status.set_level(clstatus.StatusLevel.VERBOSE)

    @QtCore.pyqtSlot(object)
    def process(self, image):
        #Image is a qimage
        #if there is any space available in the write buffer write the data

        pass


class VideoEngine(QObject):
    def __init__(self, video, actions, status):
        super (VideoEngine).__init__()
        self.s = status
        self.video = video
        self.actions = actions

        self.engine_thread = QtCore.QThread()
        self.engine_worker = VideoEngineWorker()

        self.engine_worker.moveToThread(self.engine_thread)
        self.engine_thread.start()

        QtCore.QMetaObject.invokeMethod(self.engine_worker,
                                        "thread_init",
                                        QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(object, self.video),
                                        QtCore.Q_ARG(object, self.actions))

    def setup_video(self):
        self.s.Debug("Initialize the LCD Screen")
        #Initialize the LCD Controller


    def start(self):
        print "Engine Start"
        self.s.Debug("Starting")

    def stop(self):
        self.s.Debug("Stopping")

    def reset(self):
        self.stop()
        self.setup_video()
        self.start()
