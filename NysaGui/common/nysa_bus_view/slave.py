# Distributed under the MIT licesnse.
# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#of the Software, and to permit persons to whom the Software is furnished to do
#so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

'''
Log
  6/18/2013: Initial commit
'''

import os
import sys
import json
import inspect

from PyQt4.QtCore import *
from PyQt4.QtGui import *

p = os.path.join(os.path.dirname(__file__),
                             os.pardir)

sys.path.append(p)

#from arbiter_master import ArbiterMaster

from pvg.visual_graph.box import Box
import pvg.visual_graph.graphics_utils as gu

class Slave(Box):
    """Slave Box"""

    def __init__(self,
                 scene,
                 position,
                 instance_name,
                 color,
                 parameters,
                 rect,
                 bus):

        self.bus = bus
        self.s = scene
        self.dragging = False
        super(Slave, self).__init__( position = position,
                                     scene = scene,
                                     name = instance_name,
                                     color = color,
                                     rect = rect,
                                     user_data = parameters)


        md = {}
        md["name"] = instance_name
        md["color"] = "color"
        md["data"] = parameters
        md["move_type"] = "move"
        #self.is_movable = False
        self.movable(False)

        #This will raise an error if there is an illegal bus type
        bus_type = bus.get_bus_type()
        if bus_type == "peripheral_bus":
            md["type"] = "peripheral_slave"
        elif bus_type == "memory_bus":
            md["type"] = "memory_slave"

        js = json.dumps(md)
        self.slave_data = js
        self.setAcceptDrops(False)
        self.sdbg = False

    def get_slave_tags(self):
        return json.loads(self.slave_data)

    def contextMenuEvent(self, event):

        menu_items = (("&Remove", self.remove_slave),)

        menu = QMenu(self.parentWidget())
        for text, func in menu_items:
            menu.addAction(text, func)
        menu.exec_(event.screenPos())

    def remove_slave(self):
        self.s.actions.remove_slave.emit(self.bus.get_bus_type(), self.bus.get_slave_index(self.box_name))

    def hide_arbiter_masters(self):
        pass

    def itemChange(self, a, b):
        if QGraphicsItem.ItemSelectedHasChanged == a:
            if b.toBool():
                self.s.slave_selected(self.box_name, self.bus)
            else:
                self.s.slave_deselected(self.box_name, self.bus)
        return super(Slave, self).itemChange(a, b)

    def mouseMoveEvent(self, event):
        if not self.is_movable():
            return super(Slave, self).mouseMoveEvent(event)

        if (Qt.LeftButton & event.buttons()) > 0:
            pos = event.pos()
            epos = event.buttonDownPos(Qt.LeftButton)
            l = QLineF(pos, epos)
            if (l.length() < QApplication.startDragDistance()):
                event.accept
                return

            elif not self.dragging:
                self.dragging = True
                self.hide()
                mime_data = QMimeData()
                mime_data.setData("application/flowchart-data", self.slave_data)
                 #Create and dispatch a move event
                drag = QDrag(event.widget())
                drag.start(Qt.MoveAction)
                drag.setMimeData(mime_data)

                #create an image for the drag
                size = QSize(self.start_rect.width(), self.start_rect.height())
                pixmap = QPixmap(size)
                pixmap.fill(QColor(self.color))
                painter = QPainter(pixmap)
                pen = QPen(self.style)
                pen.setColor(Qt.black)
                painter.setPen(pen)
                painter.setFont(self.text_font)
                #painter.drawText(0, 0, 100, 100, 0x24, self.box_name)

                gu.add_label_to_rect(painter, self.rect, self.box_name)
                painter.end()
                drag.setPixmap(pixmap)
                #p = QPointF(event.buttonDownScreenPos(Qt.LeftButton))
                #p = p.toPoint()
                prev_pos = self.pos()
                #print "Position: %f, %f" % (pos.x(), pos.y())
                #print "Previous Pos: %f, %f" % (prev_pos.x(), prev_pos.y())
                drag.setHotSpot(epos.toPoint())
                
                prev_index = self.bus.get_slave_index(self.box_name)
                #print "\tdrag started"
                #value = drag.exec_()
                value = drag.exec_(Qt.MoveAction)
                self.show()
                if value == 0:
                    event.accept
                else:
                    event.accept
                self.dragging = False

        super(Slave, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        #print "Slave: Mouse Release Event"
        super (Slave, self).mouseReleaseEvent(event)

    def paint(self, painter, option, widget):
        super(Slave, self).paint(painter, option, widget)
        
    def is_arbiter_master(self):
        return False
