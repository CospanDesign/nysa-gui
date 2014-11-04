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
from Queue import Queue

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import vlc
from array import array as Array
from functools import partial



CHROMA = "RV32"
WIDTH = 320
HEIGHT = 240
PITCH = WIDTH * 4

DEBUG = True



class View(QWidget):
    """A simple Media Player using VLC and Qt
    """
    def __init__(self, actions = None, status = None):
        QWidget.__init__(self)
        #self.setWindowTitle("Media Player")

        # creating a basic vlc instance
        self.instance = vlc.Instance()
        # creating an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()

        self.createUI()
        self.isPaused = False
        self.OpenFile("/home/cospan/Downloads/BigBuckBunny_320x180.mp4")

    def createUI(self):
        """Set up the user interface, signals & slots
        """
        #self.widget = QtGui.QWidget(self)
        #self.setCentralWidget(self.widget)

        # In this widget, the video will be drawn
        self.videoframe = MFrame()
        global mframe
        mframe = self.videoframe
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
        self.volumeslider.setValue(self.mediaplayer.audio_get_volume())
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
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.playbutton.setText("Play")
            self.isPaused = True
        else:
            if self.mediaplayer.play() == -1:
                self.OpenFile()
                return
            self.mediaplayer.play()
            self.playbutton.setText("Pause")
            self.timer.start()
            self.isPaused = False

    def Stop(self):
        """Stop player
        """
        self.mediaplayer.stop()
        self.playbutton.setText("Play")


    def setVolume(self, Volume):
        """Set the volume
        """
        self.mediaplayer.audio_set_volume(Volume)

    def setPosition(self, position):
        """Set the position
        """
        # setting the position to where the slider was dragged
        self.mediaplayer.set_position(position / 1000.0)
        # the vlc MediaPlayer needs a float value between 0 and 1, Qt
        # uses integer variables, so you need a factor; the higher the
        # factor, the more precise are the results
        # (1000 should be enough)

    def updateUI(self):
        """updates the user interface"""
        # setting the slider to the desired position
        self.positionslider.setValue(self.mediaplayer.get_position() * 1000)

        if not self.mediaplayer.is_playing():
            # no need to call this function if nothing is played
            self.timer.stop()
            if not self.isPaused:
                # after the video finished, the play button stills shows
                # "Pause", not the desired behavior of a media player
                # this will fix it
                self.Stop()

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

        # create the media
        self.media = self.instance.media_new(unicode(filename))
        # put the media in the media player
        self.mediaplayer.set_media(self.media)
        # parse the metadata of the file
        self.media.parse()
        # set the title of the track as window title
        self.label.setText(self.media.get_meta(0))

        self.mediaplayer.video_set_format(self.videoframe.CHROMA,
                                          self.videoframe.WIDTH,
                                          self.videoframe.HEIGHT,
                                          self.videoframe.WIDTH * self.videoframe.NUM_BYTES)

        self.mediaplayer.video_set_format_callbacks(
                                          setup_cb,
                                          None)


        val = ctypes.py_object(self.videoframe)
        #v = ctypes.cast(self.val, ctypes.c_void_p)

        '''
        self.mediaplayer.video_set_callbacks(   lock_cb,
                                                unlock_cb,
                                                display_cb,
                                                ctypes.byref(val))
        '''

        self.mediaplayer.video_set_callbacks(   self.videoframe.lock_cb,
                                                self.videoframe.unlock_cb,
                                                self.videoframe.display_cb,
                                                ctypes.byref(val))


        print "Set format"
        print ""


        '''
        if sys.platform == "linux2": # for Linux using the X Server
            self.mediaplayer.set_xwindow(self.videoframe.winId())
        elif sys.platform == "win32": # for Windows
            self.mediaplayer.set_hwnd(self.videoframe.winId())
        elif sys.platform == "darwin": # for MacOS
            self.mediaplayer.set_nsobject(self.videoframe.winId())
        '''
        print "Width: %d" % self.mediaplayer.video_get_width()
        print "Height: %d" % self.mediaplayer.video_get_height()
        print "everything is setup!"





@vlc.CallbackDecorators.VideoFormatCb
def setup_cb(opaque, chroma, width, height, pitches, lines):
    print "setup callback!"
    chroma = ctypes.create_string_buffer(CHROMA)
    width = ctypes.c_uint(WIDTH)
    height = ctypes.c_uint(HEIGHT)
    pitches = ctypes.c_uint(PITCH)
    lines = ctypes.c_uint(HEIGHT)
    return 1

image_plane = ctypes.create_string_buffer(320 * 240 * 4)
inuse = False
c = ctypes.cast(image_plane, ctypes.c_void_p)

mframe = None

@vlc.CallbackDecorators.VideoLockCb
def lock_cb(opaque, planes):
    print "lock"
    ctypes.memset(image_plane, 0, len(image_plane))
    planes = c.value
    for i in range (len(image_plane)):
        if (image_plane[i] != 0):
            print "i: %d, l: %s" % (i, image_plane[i])
    return c.value

@vlc.CallbackDecorators.VideoUnlockCb
def unlock_cb(opaque, picture, planes):
    print "unlock"

@vlc.CallbackDecorators.VideoDisplayCb
def display_cb(opaque, picture):
    if picture is None:
        return
    byte_array = ctypes.cast(picture, ctypes.POINTER(ctypes.c_byte))
    str = ctypes.string_at(picture, len(image_plane))

    a = Array('B', ctypes.string_at(picture, len(image_plane)))

class MFrame(QtGui.QFrame):
    NUM_PLANES = 10
    CHROMA = "RV32"
    WIDTH = 320
    HEIGHT = 240
    NUM_BYTES = 4
    PITCH = WIDTH * NUM_BYTES
    IMAGE_COUNT = 10

    def __init__(self):
        QtGui.QFrame.__init__(self)
        self.available_queue = Queue()
        self.busy_queue = Queue()
        self.image_queue = Queue()

        self.image_planes = []
        for i in range(self.NUM_PLANES):
            self.image_planes.append(ctypes.create_string_buffer(self.WIDTH * self.HEIGHT * self.NUM_BYTES))
            if DEBUG:
                for j in range(self.WIDTH * self.HEIGHT * self.NUM_BYTES):
                    if (i % 2) == 0:
                        self.image_planes[i][j] = "Z"
                    else:
                        self.image_planes[i][j] = "0"

        self.pointers = []
        for i in range(len(self.image_planes)):
            self.pointers.append(ctypes.cast(self.image_planes[i], ctypes.c_void_p))
            #self.pointers.append(self.image_planes[i])
            self.available_queue.put(self.pointers[i])

        #pus some values in the queues so I can find them
        self.img = None

    def paintEvent(self, e):
        print "Paint event"

        if self.image_queue.empty():
            return

        img = self.image_queue.get()
        print "image size: %d x %d" % (img.width(), img.height())
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawImage(QPoint(0, 0), img)
        qp.end()

    @vlc.CallbackDecorators.VideoUnlockCb
    def unlock_cb(user_data, picture, planes):
        print "unlock"
        self = mframe
        p = self.busy_queue.get()
        self.available_queue.put(p)

    @vlc.CallbackDecorators.VideoLockCb
    def lock_cb(user_data, planes):
        self = mframe
        print "lock"
        if self.available_queue.empty():
            return None

        p = self.available_queue.get()
        self.busy_queue.put(p)
        #return ctypes.byref(p)
        return p.value
        
    @vlc.CallbackDecorators.VideoDisplayCb
    def display_cb(user_data, picture):
        self = mframe
        print "display"
        str = ctypes.string_at(picture, len(image_plane))
        if DEBUG:
            print "str[0]: %s" % str[0]

        if self.image_queue.qsize() < self.IMAGE_COUNT:
            img = QImage(str, self.WIDTH, self.HEIGHT, QImage.Format_ARGB32_Premultiplied)
            self.image_queue.put(img)
            QtCore.QMetaObject.invokeMethod(mframe,
                                        "repaint",
                                        QtCore.Qt.QueuedConnection)


