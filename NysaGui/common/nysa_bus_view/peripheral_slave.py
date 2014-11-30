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
  6/14/2013: Initial commit
'''

import os
import sys
from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4 import QtCore
from PyQt4.QtGui import *

p = os.path.join(os.path.dirname(__file__),
                             os.pardir)

sys.path.append(p)

from pvg.visual_graph.box import Box
from slave import Slave
from arbiter_master import ArbiterMaster

from defines import SLAVE_RECT
from defines import PERIPHERAL_SLAVE_COLOR
from defines import ARB_MASTER_HORIZONTAL_SPACING
from defines import ARB_MASTER_VERTICAL_SPACING
from defines import ARB_MASTER_RECT

from defines import ARB_MASTER_ACT_RECT
from defines import ARB_MASTER_ACT_COLOR


from link import side_type as st
from link import link_type as lt
from link import Link

highlight_width = 8

class PeripheralSlave(Slave):
    """Host Interface Box"""

    def __init__(self,
                 scene,
                 instance_name,
                 parameters,
                 bus):

        self.nochange = False
        self.arbiter_master = False
        self.arbiter_boxes = []
        if scene.is_arbiter_master(instance_name):
            self.arbiter_master = True

        self.links = {}
        self.am_selected = False
        self.show_arbiter_masters_boxes = False

        self.peripheral_bus = bus
        self.ignore_selection = False
        self.dbg = False

        super(PeripheralSlave, self).__init__(position = QPointF(0.0, 0.0),
                                             scene = scene,
                                             instance_name = instance_name,
                                             color = PERIPHERAL_SLAVE_COLOR,
                                             rect = SLAVE_RECT,
                                             bus = bus,
                                             parameters = parameters)
        self.s = scene
        self.movable(False)

    def paint(self, painter, option, widget):
        pen = QPen(self.style)
        pen.setColor(Qt.black)
        pen.setWidth(1)
        if option.state & QStyle.State_Selected:
          #Selected
          pen.setColor(QColor("black"))
          pen.setWidth(highlight_width)

        painter.setPen(pen)
        painter.drawRect(self.rect)
        painter.fillRect(self.rect, QColor(self.color))

        #draw text
        r = QRectF(self.rect)


        if self.arbiter_master and not self.show_arbiter_masters_boxes:
            #Paint Arbiter
            arb_height = self.rect.height()
            arb_width  = self.rect.width() / 4
            arb_pos = QPointF(self.rect.width() - arb_width, 0)
            arb_rect = QRectF(arb_pos, QSizeF(arb_width, arb_height))
            r = QRectF(QPointF(r.x(), r.y()), QSizeF(self.rect.width() - arb_width, r.height())) 

            pen = QPen(self.style)
            pen.setColor(Qt.black)
            pen.setWidth(1)
            if option.state & QStyle.State_Selected:
                #Selected
                pen.setColor(Qt.black)
                pen.setWidth(highlight_width)

            painter.setPen(pen)
            painter.drawRect(arb_rect)
            painter.fillRect(arb_rect, QColor(Qt.white))

            painter.drawText(arb_rect, Qt.AlignCenter, "M")

        painter.setFont(self.text_font)
        pen.setColor(Qt.black)
        painter.setPen(pen)
        br = painter.fontMetrics().boundingRect(self.box_name)

        scale_x = r.width() / br.width()

        if scale_x > 1.0:
            painter.drawText(r, Qt.AlignCenter, self.box_name)
        else:
            #For the cases where the text is larger than th box
            font_height = br.height()
            box_height = r.height()
            painter.scale(scale_x, scale_x)
            br.translate(r.left() - br.left(), r.top() - br.top())
            br.translate(0.0, box_height * (0.5/scale_x) - font_height/2)
            painter.drawText(br, Qt.TextSingleLine, self.box_name)

    def update_links(self):
        if self.dbg: print "PS: update_links()"
        start = self.mapToScene(self.side_coordinates(st.right))

        for link in self.links:
            end = self.mapToScene(self.mapFromItem(link, link.side_coordinates(st.left))) 
            self.links[link].set_start_end(start, end)

    def mouseReleaseEvent(self, event):
        if self.show_arbiter_masters_boxes:
            if len(self.arbiter_boxes) == 0:
                self.show_arbiter_masters()
        return QGraphicsItem.mouseReleaseEvent(self, event)

    def itemChange(self, a, b):
        result = super(PeripheralSlave, self).itemChange(a, b)
        if self.isSelected():
            self.peripheral_bus.slave_selection_changed(self)
            if self.arbiter_master:
                self.show_arbiter_masters_boxes = True

        return result

    def clear_links(self):
        for link in self.links:
            self.scene().removeItem(self.links[link])
        self.links = {}

    def hide_arbiter_masters(self):
        self.show_arbiter_masters_boxes = False
        self.remove_arbiter_masters()

    def remove_arbiter_masters(self):
        print "PS: Removed arbiter masters"

        self.clear_links()

        for ab in self.arbiter_boxes:
            ab.remove_from_link()
            self.s.removeItem(ab)

        self.arbiter_boxes = []
        self.s.invalidate(self.s.sceneRect())

    def is_arbiter_master_selected(self):
        if self.dbg: print "PS: is_arbiter_master_selected()"
        for am in self.arbiter_boxes:
            if am.isSelected():
                return True
        return False

    def arbiter_master_selected(self, arbiter_master):
        self.dbg = True
        if self.dbg: print "PS: arbiter_master_selected()"
        if self.ignore_selection:
            return

        self.ignore_selection = True
        self.s.clearSelection()
        #Maybe this is to remove other arbiter masters!
        self.remove_arbiter_masters()
        position = QPointF(self.pos())
        rect = QRectF(self.rect)
        arb_x = position.x() + rect.width() + ARB_MASTER_HORIZONTAL_SPACING
        arb_y = position.y() + (rect.height() / 2)  - (ARB_MASTER_ACT_RECT.height() / 2)

        arb_pos = QPointF(arb_x, arb_y)
        #print "Adding arbiter master"
        am = ArbiterMaster(name = arbiter_master,
                           position = arb_pos,
                           y_pos = arb_y,
                           scene = self.scene(),
                           slave = self)

        am.set_activate(True)
        am.update_view()
        self.arbiter_boxes.append(am)
        al = Link(self, am, self.scene(), lt.arbiter_master)
        al.from_box_side(st.right)
        al.to_box_side(st.left)

        al.en_bezier_connections(True)
        self.links[am] = al

        #print "update links"
        self.update_links()
        self.ignore_selection = False
        self.s.invalidate(self.s.sceneRect())
        self.dbg = True

    def show_arbiter_masters(self):
        if len(self.arbiter_boxes) > 0:
            return
        print "show_arbiter_masters()"
        count = self.s.module_arbiter_count(self.box_name)
        print "%d arbiters" % count

        #print "Add %d arbiter boxes" % num_m

        #setup the start position for the case where there is only one master
        position = QPointF(self.pos())
        rect = QRectF(self.rect)
        arb_x = position.x() + rect.width() + ARB_MASTER_HORIZONTAL_SPACING
        arb_y = position.y() + rect.height() / 2
        arb_y -= (count - 1) * ARB_MASTER_VERTICAL_SPACING
        arb_y -= ((count - 1) * ARB_MASTER_RECT.height()) / 2

        arb_pos = QPointF(arb_x, arb_y)

        #for i in range(0, len(self.arbiter_masters)):
        for name in self.s.arbiter_master_names(self.box_name):
            #print "Add Arbiter %s" % self.arbiter_masters[i]
            arb_rect = QRectF(ARB_MASTER_RECT)

            #am = ArbiterMaster(name = self.arbiter_masters[i], 
            am = ArbiterMaster(name = name, 
                               position = arb_pos,
                               y_pos = position.y(),
                               scene = self.scene(),
                               slave = self)

            #am.movable(False)

            self.arbiter_boxes.append(am)
            al = Link(self, am, self.scene(), lt.arbiter_master)
            al.from_box_side(st.right)
            al.to_box_side(st.left)

            al.en_bezier_connections(True)
            self.links[am] = al

            #Progress the position
            arb_pos = QPointF(arb_pos.x(), arb_pos.y() + arb_rect.height() + ARB_MASTER_VERTICAL_SPACING)

        self.update_links()

    def is_arbiter_master(self):
        return self.arbiter_master


