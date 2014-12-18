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

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from array import array as Array

DEBUG = True

class View(QWidget):

    def __init__(self, actions = None, status = None):
        QWidget.__init__(self)
        self.actions = actions
        self.isPaused = False
        self.i2s = None
        self.audio_filename = "/home/cospan/sandbox/wave_file.wav"

        #Name
        self.filename_label = QLabel("")

        #Menu Bar
        open = QAction("&Open", self)
        open.triggered.connect(self.open_file)

        menubar = QMenuBar()
        menubar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        filemenu = menubar.addMenu("&File")
        filemenu.addAction(open)
        filemenu.addSeparator()
        self.label = QLabel("")
        self.label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)

        #Converter Progress
        self.convert_progress = QProgressBar()
        self.convert_progress.setRange(0, 100)
        self.actions.convert_audio_update.connect(self.convert_progress.setValue)

        #Audio Position
        self.position_slider = QSlider(Qt.Horizontal, self)
        self.position_slider.setToolTip("Position")
        self.position_slider.setMaximum(1000)
        self.position_slider.sliderMoved.connect(self.set_position)

        #Buttons
        self.play_pause_button = QPushButton("Play")
        self.play_pause_button.clicked.connect(self.play_pause)

        self.stop_button = QPushButton("stop")
        self.stop_button.clicked.connect(self.stop)

        self.test_1khz_button = QPushButton("Test 1Khz")
        self.test_1khz_button.clicked.connect(self.actions.play_1khz)

        #Setup Layout
        layout = QVBoxLayout()
        name_layout = QHBoxLayout()
        box_layout = QHBoxLayout()

        layout.addWidget(menubar)

        name_layout.addWidget(QLabel("Audio Filename:"))
        name_layout.addWidget(self.filename_label)

        box_layout.addWidget(self.play_pause_button)
        box_layout.addWidget(self.stop_button)
        box_layout.addWidget(self.test_1khz_button)

        layout.addLayout(name_layout)
        layout.addWidget(QLabel("Converting to raw progress..."))
        layout.addWidget(self.convert_progress)
        layout.addWidget(self.position_slider)
        layout.addLayout(box_layout)
        self.setLayout(layout)

    def play_pause(self):
        """Toggle play/pause status
        """
        if not self.isPaused:
            self.play_pause_button.setText("Play")
            self.isPaused = True
            self.actions.play_audio.emit()
        else:
            self.play_pause_button.setText("Pause")
            self.isPaused = False
            self.actions.pause_audio.emit()

    def stop(self):
        """stop player
        """
        self.isPaused = False
        self.play_pause_button.setText("Play")
        self.actions.stop_audio.emit()

    def open_file(self, filename=None):
        """Open a media file in a MediaPlayer
        """
        if filename is None:
            #filename = QFileDialog.getopen_fileName(self, "Open File", os.path.expanduser("~"))
            filename = QFileDialog.getopen_fileName(self,
                            "Open a Audio File", "/home/cospan/Downloads",
                            "Audio Files (*.wav)")
        if not filename:
            return

        self.filename_label = filename
        self.set_audio_file.emit(filename)

    def set_audio_filename(self, filename):
        self.filename_label.setText(filename)

    def set_position(self):
        position = (self.position_slider.value() * 1.0)
        max_position = (self.position_slider.maximum() * 1.0)
        position = position / max_position
        print "setting position to: %f" % position
        self.actions.set_audio_position.emit(position)

    def update_audio_position(self, position):
        position = position * 1.0
        max_position = (self.position_slider.maximum() * 1.0)
        position = int(position * max_position)
        print "Max Position: %d" % max_position
        print "Position: %d" % position
        #self.position_slider.setValue(position * 100)
        self.position_slider.setValue(position)

