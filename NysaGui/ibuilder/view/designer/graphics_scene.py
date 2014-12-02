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

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

p = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            os.pardir,
                                            os.pardir,
                                            os.pardir,
                                            os.pardir))

p = os.path.abspath(p)
#print "Visual Graph Path: %s" % p
sys.path.append(p)
from NysaGui.common.pvg.visual_graph.graphics_scene import GraphicsScene as gs



def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)

view_state = enum(  "normal",
                    "arbiter_master_selected")

class GraphicsScene(gs):

    def __init__(self, view, status, actions, app):
        super (GraphicsScene, self).__init__(view, app)
        self.status = status
        self.actions = actions
        self.arbiter_selected = None
        self.state = view_state.normal
        self.dbg = False
        self.prev_slave = None
        self.master = None
        self.peripheral_bus = None
        self.memory_bus = None
        if self.dbg: print "GS: Set state for normal"

    #Overriden Methods
    def box_selected(self, data):
        if data is not None:
            self.actions.module_selected.emit(data)

    def box_deselected(self, data):
        if data is not None:
            self.actions.module_deselected.emit(data)

    def remove_selected(self, reference):
        if self.dbg: print "GS: remove_selected()"

    #Overriden PyQT4 Methods
    def mouseMoveEvent(self, event):
        #print "mouse move event"
        super (GraphicsScene, self).mouseMoveEvent(event)
        self.auto_update_all_links()

    def mousePressEvent(self, event):
        #print "mouse press event"
        super (GraphicsScene, self).mousePressEvent(event)
        self.auto_update_all_links()

    def dropEvent(self, event):
        print "GS: Drop Event"
        super (GraphicsScene, self).dropEvent(event)

    def startDrag(self, event):
        print "start drag"
        if self.dbg: print "GS: Drag start event"

    def auto_update_all_links(self):
        for l in self.links:
            if l.is_center_track():
                #print "Center track!"
                #print "\tlink_ref: %s - %s" % (l.from_box.box_name, l.to_box.box_name)
                l.auto_update_center()
        if self.master is not None:
            self.master.update_master_links()
        if self.peripheral_bus is not None:
            self.peripheral_bus.update_links()
        if self.memory_bus is not None:
            self.memory_bus.update_links()

    #States
    def get_state(self):
        if self.dbg: print "GS: get_state()"
        return self.state

    def set_master(self, master):
        self.master = master

    def set_peripheral_bus(self, peripheral_bus):
        self.peripheral_bus = peripheral_bus

    def set_memory_bus(self, memory_bus):
        self.memory_bus = memory_bus

    def slave_selected(self, name, bus):
        self.actions.slave_selected.emit(name, bus.box_name)
        if self.arbiter_selected is None:
            self.state = view_state.normal
            return

        arbiter_name = self.arbiter_selected.box_name

        print "check for arbiter selected"
        self.state = view_state.arbiter_master_selected
        if str(name).lower() == "drt":
            self.status.Info("Can't attach to the DRT")
            return

        from_slave = self.arbiter_selected.get_slave()
        from_slave_name = from_slave.box_name
        if from_slave_name == name:
            self.status.Info("Can't attach to ourselves")
            return

        aribiter_name = self.arbiter_selected.box_name
        to_slave = bus.get_slave(name)
        to_slave_name = name
        print "connect %s - %s - %s" % (from_slave_name, aribiter_name, to_slave_name)

        connected_slave = self.get_arbiter_master_connected(from_slave_name, arbiter_name)
        if connected_slave is not None:
            if connected_slave.box_name == to_slave_name:
                return
            print "arbiter is already connected to %s" % connected_slave.box_name
            print "disconnecting"
            #self.arbiter_master_disconnect(self.arbiter_selected, connected_slave)
            self.arbiter_master_disconnect(self.arbiter_selected, connected_slave)

        self.controller.connect_arbiter_master(from_slave_name, to_slave_name, arbiter_name)
        self.arbiter_selected.update_view()
        self.arbiter_selected.connect_slave(to_slave)
        #self.arbiter_selected.add_link(to_slave)

    def slave_deselected(self, name, bus):
        self.actions.slave_deselected.emit(name, bus.box_name)
        if self.state == view_state.normal:
            self.prev_slave = bus.get_slave(name)
            self.prev_slave.hide_arbiter_masters()

    #Arbiter Interface
    def is_arbiter_master(self, module_name):
        if self.controller is None:
            self.status.Verbose("controller is not connected!")
            return False
        return self.controller.is_arbiter_master(module_name)

    def is_arbiter_master_connected(self, module_name, arbiter_name = None):
        if self.controller is None:
            self.status.Verbose("controller is not connected!")
            return False
        return self.controller.is_arbiter_master_connected(module_name, arbiter_name)

    def module_arbiter_count(self, module_name):
        if self.controller is None:
            self.status.Verbose("controller is not connected!")
            return False
        return self.controller.module_arbiter_count(module_name)

    def arbiter_master_names(self, module_name):
        if self.controller is None:
            self.status.Verbose("controller is not connected")
            return []
        return self.controller.arbiter_master_names(module_name)

    def connect_arbiter_master(self, from_module_name, to_module_name, arbiter_name):
        if self.controller is None:
            self.status.Verbose("controller is not connected!")
            return
        self.controller.connect_arbiter_master(from_module_name, to_module_name, arbiter_name)

    def disconnect_arbiter_master(from_module_name, to_module_name = None, arbiter_name = None):
        if self.controller is None:
            self.status.Verbose("controller is not connected!")
            return
        self.controller.disconnect_arbiter_master(from_module_name, to_module_name, arbiter_name)

    def get_connected_arbiter_name(self, from_module_name, to_module_name):
        if self.controller is None:
            self.status.Verbose("controller is not connected!")
            return ""
        return self.controller.get_connected_arbiter_name(from_module_name, to_module_name)

    def is_modules_connected_through_arbiter(self, from_module_name, to_module_name):
        if self.controller is None:
            self.status.Verbose("controller is not connected!")
            return False
        return self.controller.is_modules_connected_through_arbiter(from_module_name, to_module_name)

    def is_arbiter_master_active(self):
        if self.dbg: print "GS: is_arbiter_master_active()"
        #return self.state == view_state.arbiter_master_selected
        return self.arbiter_selected is not None

    def arbiter_master_selected(self, slave, arbiter_master):
        print "GS: arbiter_master_selected()"
        name = arbiter_master.box_name
        self.state = view_state.arbiter_master_selected
        if self.dbg: print "\tSet state for arbiter master"
        self.arbiter_selected = arbiter_master
        self.peripheral_bus.enable_expand_slaves(name, True)
        self.memory_bus.enable_expand_slaves(name, True)
        slave.arbiter_master_selected(name)

    def arbiter_master_deselected(self, arbiter_master):
        print "GS: arbiter_master_deselected()"
        #for i in range (len(self.links)):
        #    self.removeItem(self.links[i])
        self.arbiter_selected.remove_from_link()
        self.arbiter_selected.remove_to_link()
        #self.links = []
        self.arbiter_selected = None
        name = arbiter_master.box_name
        self.state = view_state.normal
        print "\tset state for normal"
        self.peripheral_bus.enable_expand_slaves(name, False)
        self.memory_bus.enable_expand_slaves(name, False)
        slave = arbiter_master.get_slave()
        #slave.remove_arbiter_masters()
        slave.hide_arbiter_masters()
        #slave.show_arbiter_masters()
        #slave.setSelected(True)

    def is_arbiter_master_selected(self):
        if self.dbg: print "GS: is_arbiter_master_selected()"
        return self.arbiter_selected is not None

    def get_arbiter_master_selected(self):
        if self.dbg: print "GS: get_arbiter_master_selected()"
        return self.arbiter_selected

    def arbiter_master_disconnect(self, arbiter_master, to_slave):
        if self.dbg: print "GS: arbiter_master_disconnect()"
        from_slave = arbiter_master.get_slave()
        arbiter_name = arbiter_master.box_name
        if self.dbg: print "\tarbiter_master: %s" % arbiter_master.box_name

        #XXX: Remove the arbiter connctor
        self.controller.disconnect_arbiter_master(from_slave.box_name, to_slave.box_name, arbiter_name)
        #Remove the visual connection
        arbiter_master.disconnect_slave()

    def get_arbiter_master_connected(self, from_slave, arbiter_name):
        to_bus, to_slave_name = self.controller.get_arbiter_master_connected(from_slave, arbiter_name)
        if to_slave_name is None:
            return None

        to_slave_node = None
        if to_bus == "peripheral":
            to_slave_node = self.peripheral_bus.get_slave(to_slave_name)
        else:
            to_slave_node = self.memory_bus.get_slave(to_slave_name)
            
        return to_slave_node

    def clear_links(self):
        self.links = []

    def show_arbiters(self):
        return True


