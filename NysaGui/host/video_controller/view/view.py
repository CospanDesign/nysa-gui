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


""" nysa interface
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os
import time
import ctypes
import math
from Queue import Queue

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from array import array as Array

CV2_FOUND = False

try: 
    import numpy as np
    import cv2
    CV2_FOUND = True
except Exception:
    CV2_FOUND = False



CHROMA = "RV32"
WIDTH = 480
HEIGHT = 272
BYTE_COUNT = 4
PITCH = WIDTH * BYTE_COUNT

DEBUG = True

class View(QWidget):
    """A simple Media Player using VLC and Qt
    """
    def __init__(self, actions = None, status = None):
        QWidget.__init__(self)
        self.actions = actions
        self.createUI()
        self.isPaused = False
        #self.OpenFile("/home/cospan/Downloads/BigBuckBunny_320x180.mp4")
        self.OpenFile("/home/cospan/Downloads/big_buck_bunny_480p_surround-fix.avi")
        self.lcd = None

    def set_lcd(self, lcd):
        self.lcd = lcd
        self.videoframe.set_lcd(lcd)

    def createUI(self):
        """Set up the user interface, signals & slots
        """
        if CV2_FOUND:
            self.videoframe = CV2_VideoDisplay()
        else:
            self.videoframe = VideoDisplay()

        self.palette = self.videoframe.palette()
        self.palette.setColor (QtGui.QPalette.Window,
                               QtGui.QColor(0,0,0))
        self.videoframe.setPalette(self.palette)
        self.videoframe.setAutoFillBackground(True)

        self.positionslider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.positionslider.setToolTip("Position")
        self.positionslider.setMaximum(1000)
        self.connect(self.positionslider,
                     QtCore.SIGNAL("sliderMoved(int)"), self.setPosition)

        self.hbuttonbox = QtGui.QHBoxLayout()
        self.playbutton = QtGui.QPushButton("Play")
        self.hbuttonbox.addWidget(self.playbutton)
        self.connect(self.playbutton, QtCore.SIGNAL("clicked()"),
                     self.PlayPause)

        self.stopbutton = QtGui.QPushButton("Stop")
        self.hbuttonbox.addWidget(self.stopbutton)
        self.connect(self.stopbutton, QtCore.SIGNAL("clicked()"),
                     self.Stop)

        camera_button = QtGui.QPushButton("Camera")
        camera_button.clicked.connect(self.camera_play)
        self.hbuttonbox.addWidget(camera_button)

        color_test_button = QtGui.QPushButton("Color Test")
        self.connect(color_test_button, QtCore.SIGNAL("clicked()"), self.actions.color_test)
        #self.actions.color_test.connect(color_test_button.connect)
        self.hbuttonbox.addWidget(color_test_button)



        self.hbuttonbox.addStretch(1)
        self.volumeslider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.volumeslider.setMaximum(100)

        #self.volumeslider.setValue(self.mediaplayer.audio_get_volume())
        self.volumeslider.setToolTip("Volume")
        self.hbuttonbox.addWidget(self.volumeslider)
        self.connect(self.volumeslider,
                     QtCore.SIGNAL("valueChanged(int)"),
                     self.setVolume)


        open = QtGui.QAction("&Open", self)
        self.connect(open, QtCore.SIGNAL("triggered()"), self.OpenFile)

        menubar = QtGui.QMenuBar()
        menubar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        filemenu = menubar.addMenu("&File")
        filemenu.addAction(open)
        filemenu.addSeparator()
        self.label = QLabel("")
        self.label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        
        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.addWidget(menubar)
        self.vboxlayout.addWidget(self.label)
        self.videoframe.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)


        self.vboxlayout.addWidget(self.videoframe)
        self.vboxlayout.addWidget(self.positionslider)
        self.vboxlayout.addLayout(self.hbuttonbox)

        self.setLayout(self.vboxlayout)
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(200)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"),
                     self.updateUI)

    def camera_play(self):
        print "play the camera"
        self.videoframe.camera_go()

    def PlayPause(self):
        """Toggle play/pause status
        """
        if not self.isPaused:
            self.playbutton.setText("Play")
            self.isPaused = True
            self.videoframe.play()
        else:
            self.playbutton.setText("Pause")
            self.isPaused = False
            self.videoframe.stop()

    def Stop(self):
        """Stop player
        """
        self.isPaused = False
        self.playbutton.setText("Play")
        print "STOPPING!"
        self.videoframe.stop()

    def setVolume(self, Volume):
        """Set the volume
        """
        print "volume"

    def setPosition(self, position):
        """Set the position
        """
        pass

    def updateUI(self):
        """updates the user interface"""
        # setting the slider to the desired position
        self.positionslider.setValue(0 * 1000)

    def OpenFile(self, filename=None):
        """Open a media file in a MediaPlayer
        """
        if filename is None:
            #filename = QtGui.QFileDialog.getOpenFileName(self, "Open File", os.path.expanduser("~"))
            filename = QtGui.QFileDialog.getOpenFileName(self,
                            "Open a Video File", "/home/cospan/Downloads",
                            "Video Files (*.mpg *.avi *.mp4 *.ogg)")


        if not filename:
            return

        
        self.videoframe.open_file(filename)

        self.label.setText(filename)

class VideoWorker(QObject):
    def __init__(self):
        super(VideoWorker, self).__init__()

    @QtCore.pyqtSlot(object, object)
    def thread_init(self,
                    video_display,
                    video_capture):
        print "Iniitialize Video Player"
        self.video_display = video_display
        self.video_capture = video_capture
        self.start = False
        self.lcd = None

    @QtCore.pyqtSlot(object)
    def set_lcd(self, lcd):
        self.lcd = lcd

    @QtCore.pyqtSlot()
    def stop_video(self):
        print "VW: Stopping"
        self.stop = True

    @QtCore.pyqtSlot()
    def camera_go(self):
        self.stop = False
        while (not self.stop):
            ret, frame = self.video_capture.read()
            if ret == False:
                self.stop = True
                break
            frame  = cv2.resize(frame, dsize=(WIDTH, HEIGHT))  
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGRA)
            if self.lcd is not None:
                data = Array('B', frame.tostring())
                self.lcd.dma_writer.write(data)
            QtCore.QMetaObject.invokeMethod(self.video_display,
                                            "update_paint",
                                            QtCore.Qt.QueuedConnection,
                                            Q_ARG(object, frame))

        self.stop = False

    @QtCore.pyqtSlot(float)
    def process(self, timer):

        self.stop = False
        while (not self.stop):
            ret, frame = self.video_capture.read()
            if ret == False:
                self.stop = True
                break
            frame  = cv2.resize(frame, dsize=(WIDTH, HEIGHT))  
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGRA)
            if self.lcd is not None:
                data = Array('B', frame.tostring())
                self.lcd.dma_writer.write(data)
            QtCore.QMetaObject.invokeMethod(self.video_display,
                                            "update_paint",
                                            QtCore.Qt.QueuedConnection,
                                            Q_ARG(object, frame))

class VideoDisplay(QWidget):
    def __init__(self):
        super(VideoDisplay, self).__init__()

    def paintEvent(self, e):
        super(VideoDisplay, self).paintEvent(e)

    def open_file(self, filename):
        pass

    def play(self):
        pass

    def stop(self):
        pass


class CV2_VideoDisplay(VideoDisplay):

    def __init__(self):
        super(CV2_VideoDisplay, self).__init__()
        self.video_capture = cv2.VideoCapture()
        #fourcc = cv2.cv.CV_FOURCC('R','V','3','2')
        #self.video_capture.set(cv2.cv.CV_CAP_PROP_FOURCC, fourcc)
        self.framerate = 1
        self.ready = False
        self.vt = QtCore.QThread()
        self.vw = VideoWorker()
        self.vw.moveToThread(self.vt)
        self.vt.start()

        QtCore.QMetaObject.invokeMethod(self.vw,
                                        "thread_init",
                                        QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(object, self),
                                        QtCore.Q_ARG(object, self.video_capture))
        self.lcd = None
        print "out of init"
        self.data = Array('B')

    def set_lcd(self, lcd):
        QtCore.QMetaObject.invokeMethod(self.vw, 
                                        "set_lcd",
                                        QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(object, lcd))
        self.lcd = lcd

    @pyqtSlot(object)
    def update_paint(self, frame):
        self.frame = frame
        self.repaint()

    def paintEvent(self, e):

        if not self.ready:
            return

        #ret, frame = self.video_capture.read()
        #if ret == False:
        #    print "stop"
        #    self.ready = False
            #self.stop()

        #im = QtGui.QImage(self.frame, WIDTH, HEIGHT, QtGui.QImage.Format_RGB888)
        im = QtGui.QImage(self.frame, WIDTH, HEIGHT, QtGui.QImage.Format_ARGB32)
        
        #im = QtGui.QImage(self.frame, WIDTH, HEIGHT, QtGui.QImage.Format_RGB32)

        #im = QtGui.QImage(self.frame, WIDTH, HEIGHT, QtGui.QImage.Format_RGB888)
        #print "Frame type: %s" % str(type(frame))
        im = im.rgbSwapped()
        '''

        frame2  = cv2.resize(frame, dsize=(WIDTH, HEIGHT))  
        frame3 = cv2.cvtColor(frame2, cv2.COLOR_RGB2RGBA)
        #print "type: frame2: %s" % str(type(frame2))
        if self.lcd is not None:
            #data = Array('B', frame2.reshape(len(frame2)).tolist())
            #self.lcd.dma_writer.write(data)
            #print "type of data: %s" % str(type(frame2.tostring))
            #self.lcd.dma_writer.write(frame2.data)
            #data = Array('B', frame3.tostring('C'))
            data = Array('B', frame3.tostring())
            self.lcd.dma_writer.write(data)
            #self.lcd.dma_writer.write(frame2.tostring())
        '''
            


        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawImage(QPoint(0, 0), im)
        qp.end()

    def open_file(self, filename):
        print "open files"
        self.video_capture.open(filename)
        #fourcc = self.video_capture.get(cv2.cv.CV_CAP_PROP_FOURCC)
        self.framerate = self.video_capture.get(cv2.cv.CV_CAP_PROP_FPS)
        if math.isnan(self.framerate):
            self.framerate = 24
        width = self.video_capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
        height = self.video_capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
        print "frame rate: %f" % self.framerate
        print "Width: %f" % width
        print "Height: %f" % height

    def play(self):
        print "play"
        val = 1.0 / self.framerate
        #val = 1.0 / 30
        #val = 1.0 / 60
        self.ready = True
        QtCore.QMetaObject.invokeMethod(self.vw,
                                        "process",
                                        QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(float, val))

    def stop(self):
        QtCore.QMetaObject.invokeMethod(self.vw,
                                        "stop_video",
                                        QtCore.Qt.QueuedConnection)
        self.vw.stop_video()

    def camera_go(self):
        self.ready = True
        self.video_capture.open(0)

        QtCore.QMetaObject.invokeMethod(self.vw,
                                        "camera_go",
                                        QtCore.Qt.QueuedConnection)


