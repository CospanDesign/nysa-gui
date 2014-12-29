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

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QTextEdit

import numpy as np
import pyqtgraph as pg

class ADCVisualizationException(Exception):
    pass

class View(QWidget):

    def __init__(self, status = None, Actions = None):
        super (View, self).__init__()

        self.setWindowTitle("Standalone View")
        self.plots = {}

        layout = QVBoxLayout()
        self.plot_widget = pg.PlotWidget(name="ADC Output")
        self.plot_widget.setLabel('left', 'Value', units='V')
        self.plot_widget.setLabel('bottom', 'Time', units='s')
        #XXX: This should be changed relative to the max, min value of the ADC
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)

        #XXX: Demo data
        self.time_window = 100
        self.set_range(0, 0, self.time_window, 100)
        self.add_plot("demo", 0, 0, self.time_window, 100)
        yd, xd = self.init_demo_data(self.time_window)
        self.set_plot_data("demo", xd, yd)

    def get_time_window(self):
        return self.time_window

    def set_range(self, min_x, min_y, max_x, max_y):
        self.time_window = max_x
        self.plot_widget.setXRange(min_x, max_x)
        self.plot_widget.setYRange(min_y, max_y)

    def add_plot(self, name = "", min_x = 0, min_y = 0, max_x = 100, max_y = 100):
        if name in self.plots:
            raise ADCVisualizationException("%s already exists!" % name)
        self.plots[name] = {"graph":self.plot_widget.plot(), "x":[], "y":[]}
        self.plots[name]["graph"].setPen(128, 0, 255)

    def set_plot_data(self, name, x_values, y_values):
        self.plots[name]["x"] = x_values
        self.plots[name]["y"] = y_values
        self.plots[name]["graph"].setData(y=y_values, x=x_values)

    def append_data(self, name, x_value, y_value):
        x_value = int(x_value % self.time_window)
        self.plots[name]["y"][x_value] = y_value
        self.plots[name]["graph"].setData(self.plots[name]["x"], self.plots[name]["y"])

    def init_demo_data(self, length):
        data = np.random.randint(100, size=length)
        return data, np.arange(0, length)
        
