# Distributed under the MIT licesnse.
# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


#A huge thanks to 'Rapid GUI Programming with Python and Qt' by Mark Summerfield

'''
Log
  7/20/2013: Initial commit
'''
import os
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

p = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            os.pardir,
                                            os.pardir,
                                            os.pardir,
                                            os.pardir))

p = os.path.abspath(p)
sys.path.append(p)
from NysaGui.common.pvg.visual_graph.graphics_view import GraphicsView as gv


class GraphicsView(gv):
    def __init__(self, actions, status, parent):
        super(GraphicsView, self).__init__(parent)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        #self.setAcceptDrops(True)
        self.initialize = True
        self.scale_min = 0.05
        self.scale_max = 15

    def mousePressEvent(self, event):
        super(GraphicsView, self).mousePressEvent(event)

    def paint(self, painter, option, widget):
        super(GraphicsView, self).paint(painter, option, widget)
        if self.initialize:
            self.update()

    def fit_in_view(self):
        self.fitInView(self.scene().sceneRect(), Qt.KeepAspectRatio)

    def update(self):
        self._scale_fit()
        self.initialize = False
        super (GraphicsView, self).update()


