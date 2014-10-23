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
UART Controller
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
from nysa.host.driver.sf_camera import SFCamera


class CameraEngineError(Exception):
    pass

class CameraEngineWorker(QObject):

    def __init__(self):
        super (CameraEngineWorker, self).__init__()

    @QtCore.pyqtSlot(int, int)
    def set_size(self, width, height):
        self.width = width
        self.height = height

    @QtCore.pyqtSlot(object)
    def set_image_format(self, image_format):
        self.image_format = image_format

    @QtCore.pyqtSlot(object, object, int, int)
    def thread_init(self,
                    camera,
                    actions,
                    width,
                    height):

        print "Initialize camera_engine_worker"
        self.camera = camera
        self.actions = actions
        self.width = width
        self.height = height
        self.image_format = None
        self.status = clstatus.Status()
        self.status.set_level(clstatus.StatusLevel.VERBOSE)
        #Connect to the interrupt of device
        #self.camera.register_interrupt_callback(self.process)

    @QtCore.pyqtSlot()
    def process(self):
        #Sanity Check
        if self.width == 0:
            self.width = 640
        if self.height == 0:
            self.height = 480
        if self.image_format is None:
            self.image_format = QImage.Format_RGB16

        data = self.camera.dma_reader.async_read()
        print "Length of data: %d" % len(data)

        qimage = QImage(data, self.width, self.height, self.image_format)
        self.actions.sf_camera_read_ready.emit(qimage)

class CameraEngine(QObject):
    def __init__(self, camera, actions, status):
        super (CameraEngine, self).__init__()
        self.camera = camera
        self.actions = actions
        self.status = status
        self.status.Verbose("Started")

        #Get rid of any previous interrupt callback
        self.camera.unregister_interrupt_callback(None)
        
        self.engine_thread = QtCore.QThread()
        self.engine_worker = CameraEngineWorker()

        self.engine_worker.moveToThread(self.engine_thread)
        self.engine_thread.start()

        QtCore.QMetaObject.invokeMethod(self.engine_worker,
                                        "thread_init",
                                        QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(object, self.camera),
                                        QtCore.Q_ARG(object, self.actions),
                                        QtCore.Q_ARG(int, self.camera.get_width()),
                                        QtCore.Q_ARG(int, self.camera.get_height()));
        #self.setup_camera()
        #self.set_size(self.camera.get_width(), self.camera.get_height())
        print "Height: %d" % self.camera.get_height()
        print "Width : %d" % self.camera.get_width()



    def setup_camera(self):
        self.status.Debug("Initialize the camera")
        self.camera.set_control(0x00)
        self.camera.reset_camera()
        self.camera.set_rgb_mode()
        self.camera.reset_counts()
        time.sleep(0.5)
        row_count = self.camera.read_row_count()
        pixel_count = self.camera.read_pixel_count()

        height = row_count
        width = pixel_count / 2
        #self.status.Debug("Height: %d" % height)
        #self.status.Debug("Width : %d" % width)

    def start(self):
        print "Engine start!"
        self.status.Debug("Starting")
        #Reset any interrupts
        self.camera.enable_camera(True)
        time.sleep(0.1)
        self.camera.start_async_reader(self.dma_reader_callback)

    def stop(self):
        self.status.Debug("Stopping")
        self.camera.enable_camera(False)
        self.camera.stop_async_reader()

    def reset(self):
        self.stop()
        self.setup_camera()
        self.start()

    '''
    def set_size(self, width, height):
        QtCore.QMetaObject.invokeMethod(self.engine_worker,
                                        "set_size",
                                        QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(int, width),
                                        QtCore.Q_ARG(int, height))


    def set_image_format(self, image_format):
        QtCore.QMetaObject.invokeMethod(self.engine_worker,
                                        "set_image_format",
                                        QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(object, image_format))


    '''
    def dma_reader_callback(self):
        print "camera engine callback"
        QtCore.QMetaObject.invokeMethod(self.engine_worker,
                                        "process",
                                        QtCore.Qt.QueuedConnection)

