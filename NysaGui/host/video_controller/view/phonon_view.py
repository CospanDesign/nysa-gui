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

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.phonon import Phonon

class View(QWidget):

    def __init__(self, status = None, Actions = None):
        super (View, self).__init__()
        self.file_path = "/home/cospan/Projects/python/pyqt/examples/i.mpg"
        self.ms = None
        self.mo = None
        self.setup_video_view()

    def setup_video_view(self):
        self.setWindowTitle("Video Controller View")
        layout = QHBoxLayout()

        #DEMO WIDGET START
        self.te = QLineEdit()
        self.te.setText(self.file_path)
        self.path_button = QPushButton("Set Path")
        self.path_button.clicked.connect(self.path_button_clicked)
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop)
        #self.vw = Phonon.VideoWidget()
        self.vw = VW()
        #self.vw = VideoDevice()

        #Puth a path at the top
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.te)
        path_layout.addWidget(self.path_button)

        #Video Layout
        video_layout = QVBoxLayout()
        video_layout.addLayout(path_layout)
        video_layout.addWidget(self.vw)

        #Controls Layout
        controls_layout = QVBoxLayout()
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.stop_button)

        #Put a video player
        layout.addLayout(video_layout)
        layout.addLayout(controls_layout)

        self.setLayout(layout)
        self.update_path()
        self.show()

    def play(self):
        self.mo.play()
        print "Background Mode: %s" % str(self.vw.backgroundRole())
        p = self.vw.paintEngine().paintDevice()
        print "Paint device: %s" % str(p)
        p = self.vw.paintEngine().paintDevice()
        print "Paint engine: %s" % str(p)


    def stop(self):
        self.mo.stop()

    def path_button_clicked(self):
        self.file_path = QFileDialog.getOpenFileName(self,
                            "Open a Video File", "/home/cospan/Downloads",
                            "Video Files (*.mpg *.avi *.mp4 *.ogg)")

        self.update_path()

    def update_path(self):
        self.te.setText(self.file_path)
        self.ms = Phonon.MediaSource(self.file_path)
        self.mo = Phonon.MediaObject()
        self.mo.setCurrentSource(self.ms)

        Phonon.createPath(self.mo, self.vw)
        audio_out = Phonon.AudioOutput(Phonon.VideoCategory)
        Phonon.createPath(self.mo, audio_out)


class VW(Phonon.VideoWidget):

    def __init__(self):
        super (VW, self).__init__()
        #print str(dir(Phonon.VideoWidget))
        self.setBackgroundRole(QPalette.NoRole)
        #self.setStyleSheet("background-color:blue;")
        #self.setStyleSheet("background-color:blue;color:green;")

    def tick(self, val):
        print "tick changed!: %d" % val
        super (VW, self).tick(val)
        
        
    def paintEngine(self):
        print "paint engine"
        return super (VW, self).paintEngine()
        
    def update(self):
        print "update"
        super (VW, self).update()

    def paintEvent(self, e):
        print "Paint event"
        super (VW, self).paintEvent(e)

    def render(self, paint_device, point = QPoint(), region=QRegion(), render_flags=QWidget.DrawWindowBackground | QWidget.DrawChildren):
        print "render 1"
        super (VW, self).render(paint_device, point, region, render_flags)

    def render(self, painter, point = QPoint(), region=QRegion(), render_flags=QWidget.DrawWindowBackground | QWidget.DrawChildren):
        print "render 2"
        super (VW, self).render(painter, point, region, render_flags)

    def event(self, e):
        #print "event: %s" % str(e)
        return super(VW, self).event(e)


    def repaint(self):
        print "Repaint 1"
        super (VW, self).repaint()

    def repaint(self, a, b, c, d):
        print "Repaint 2"
        super(VW, self).repaint(a, b, c, d)

    def repaint(self, rect):
        print "Repaint 3"
        super(VW, self).repaint(rect)


#class VideoDevice(QWidget, Phonon.AbstractVideoOutput):
class VideoDevice(QWidget, Phonon.AbstractVideoOutput):
    def __init__(self):
        QWidget.__init__(self)
        Phonon.AbstractVideoOutput.__init__(self)

    def handleConnectToMediaObject(self, mo):
        print "hi"
        pass

    def handleDisconnectFromMediaObject(mo):
        print "hi"
        pass

    def handleAddToMedia(m):
        print "hi"
        pass

    def aspectRatio (self):
        return Phonon.VideoWidget.AspectRatio4_3
    def brightness (self):
        return 1.0

    def contrast(self):
        return 0.5

    def enterFullScreen(self):
        pass

    def event (self, e):
        return super(VideoDevice, self).event(e)

    def exitFullScreen (self):
        pass

    def hue (self):
        return 0.5

    def mouseMoveEvent (self, me):
        super(VideoDevice, self).mouseMoveEvent(me)

    def saturation (self):
        return 0.5

    def scaleMode (self):
        return Phonon.VideoWidget.FitInView

    def setAspectRatio (self, ar):
        pass

    def setBrightness (self, value):
        pass

    def setContrast (self, value):
        pass

    def setFullScreen (self, fullscreen):
        pass

    def setHue (self, value):
        pass

    def setSaturation (self, value):
        pass

    def setScaleMode (self, scale_mode):
        pass

    def snapshot (self):
        return QImage()
        
