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

__author__ = 'email@example.com (name)'

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
except ModuleNotFound:
    CV2_FOUND = False



CHROMA = "RV32"
WIDTH = 320
HEIGHT = 240
BYTE_COUNT = 4
PITCH = WIDTH * BYTE_COUNT

DEBUG = True

class View(QWidget):
    """A simple Media Player using VLC and Qt
    """
    def __init__(self, actions = None, status = None):
        QWidget.__init__(self)
        self.createUI()
        self.isPaused = False
        #self.OpenFile("/home/cospan/Downloads/BigBuckBunny_320x180.mp4")
        self.OpenFile("/home/cospan/Downloads/big_buck_bunny_480p_surround-fix.avi")

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
        exit = QtGui.QAction("&Exit", self)
        self.connect(exit, QtCore.SIGNAL("triggered()"), sys.exit)



        menubar = QtGui.QMenuBar()
        menubar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        filemenu = menubar.addMenu("&File")
        filemenu.addAction(open)
        filemenu.addSeparator()
        filemenu.addAction(exit)
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

    @QtCore.pyqtSlot(object)
    def thread_init(self,
                    video_display):
        print "Iniitialize Video Player"
        self.video_display = video_display
        self.start = False

    @QtCore.pyqtSlot()
    def stop(self):
        self.stop = True

    @QtCore.pyqtSlot(float)
    def process(self, timer):
        print "process"
        self.stop = False
        
        print "timer: %f" % timer
        while (not self.stop):
            #print "next image"
            time.sleep(timer)
            QtCore.QMetaObject.invokeMethod(self.video_display,
                                            "repaint",
                                            QtCore.Qt.QueuedConnection)
        self.stop = False

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
        self.framerate = 1
        self.ready = False
        self.vt = QtCore.QThread()
        self.vw = VideoWorker()
        self.vw.moveToThread(self.vt)
        self.vt.start()

        QtCore.QMetaObject.invokeMethod(self.vw,
                                        "thread_init",
                                        QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(object, self))
        print "out of init"

    def paintEvent(self, e):

        if not self.ready:
            return

        ret, frame = self.video_capture.read()
        if ret == False:
            print "stop"
            self.ready = False
            #self.stop()

        #print "Frame type: %s" % str(type(frame))

        frame2  = cv2.resize(frame, dsize=(WIDTH, HEIGHT))  
        im = QtGui.QImage(frame2, WIDTH, HEIGHT, QtGui.QImage.Format_RGB888)

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
        self.ready = True
        QtCore.QMetaObject.invokeMethod(self.vw,
                                        "process",
                                        QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(float, val))

    def stop(self):
        QtCore.QMetaObject.invokeMethod(self.vw,
                                        "stop",
                                        QtCore.Qt.QueuedConnection)


