# -*- coding: utf-8 -*-

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
  6/10/2013: Initial commit
'''


import sys
import os
import sys
import json
import copy


from PyQt4.QtCore import *
from PyQt4.QtGui import *

import controller

from defines import PS_COLOR
from defines import MS_COLOR

from host_interface import HostInterface
from master import Master
from peripheral_bus import PeripheralBus
from memory_bus import MemoryBus
from peripheral_slave import PeripheralSlave
from memory_slave import MemorySlave

from nysa.ibuilder.lib import utils
from nysa.ibuilder.lib import verilog_utils as vutils
from nysa.ibuilder.lib import wishbone_utils
from nysa.ibuilder.lib import ibuilder_error

from NysaGui.common.graph.graph_manager import NodeType
from NysaGui.common.graph.graph_manager import SlaveType
from .wishbone_model import WishboneModel

class WishboneController (controller.Controller):

    def __init__(self, config_dict, scene, status):
        self.s = status
        self.model = WishboneModel(config_dict)
        self.scene = scene

        super(WishboneController, self).__init__(self.model, status)
        self.s.Debug( "Wishbone controller started")
        self.bus = "wishbone"
        if "INTERFACE" not in config_dict.keys():
            self.model.set_default_board_project(config_dict["board"])
        else:
            self.model.load_config_dict(config_dict)
        #self.model.initialize_graph(debug = True)
        self.model.initialize_graph(debug = False)
        #self.initialize_view()

    def initialize_view(self):
        self.s.Debug( "Add Master")
        m = Master(scene = self.scene)
        self.boxes["master"] = m

        self.s.Debug( "Add Host Interface")
        hi_name = self.model.get_host_interface_name()
        hi = HostInterface(self.scene,
                           hi_name)
        hi.link_master(m)
        self.boxes["host_interface"] = hi

        self.s.Debug( "Add Peripheral Bus")
        pb = PeripheralBus(self.scene,
                           m)
        m.link_peripheral_bus(pb)
        self.boxes["peripheral_bus"] = pb

        self.s.Debug( "Add Memory Bus")
        mb = MemoryBus(self.scene,
                       m)
        self.boxes["memory_bus"] = mb
        m.link_memory_bus(mb)
        self.editable = False
        self.refresh_slaves()
        #self.initialize_bindings()

    def refresh_slaves(self, editable = None):
        if editable is None:
            editable = self.editable
        else:
            self.editable = editable
            
        self.s.Debug("WBC: refresh_slaves")
        #Create a list of slaves to send to the bus
        slave_type = SlaveType.PERIPHERAL
        nslaves = self.model.get_number_of_slaves(slave_type)
        slave_list = []
        paths = utils.get_local_verilog_paths()
        for i in range(nslaves):
            sitem = {}
            sitem["instance_name"] = self.model.get_slave_name(slave_type, i)
            #print "peripheral instance name: %s" % self.model.get_slave_name(slave_type, i)
            #sitem["parameters"] = self.model.get_slave_parameters(slave_type, i)
            slave_list.append(sitem)

        pb = self.boxes["peripheral_bus"]
        #update the bus
        self.s.Debug("updating slave view")
        pb.update_slaves(slave_list, editable)

        slave_type = SlaveType.MEMORY
        nslaves = self.model.get_number_of_slaves(slave_type)
        slave_list = []
        for i in range(nslaves):
            sitem = {}
            sitem["instance_name"] = self.model.get_slave_name(slave_type, i)
            #print "memory instance name: %s" % self.model.get_slave_name(slave_type, i)
            #sitem["parameters"] = self.model.get_slave_parameters(slave_type, i)
            slave_list.append(sitem)

        mb = self.boxes["memory_bus"]
        #update the bus
        self.s.Debug("WBC: updating slave view")
        mb.update_slaves(slave_list, editable)

    def enable_editing(self):
        self.editable = True
        self.refresh_slaves()

    def disable_editing(self):
        self.editable = False
        self.refresh_slaves()

    def drag_move(self, event):
        #print "Drag movvve"
        if event.mimeData().hasFormat("application/flowchart-data"):
            event.accept()
        else:
            event.ignore()

    def find_slave_position(self, drop_position):
        self.s.Debug("Looking for slave position")
        return drop_position

    def drag_enter(self, event):
        '''
        An item has entered the canvas
        '''
        if event.mimeData().hasFormat("application/flowchart-data"):
            self.s.Debug("Detect box")
            event.accept()
        else:
            event.ignore()

    def drag_leave(self, event):
        #print "leave :("
        event.ignore()
        '''
        if event.mimeData().hasFormat("application/flowchart-data"):
            self.s.Debug("Detect box")
            event.accept()
        else:
            event.ignore()
        '''

    def drag_move(self, event):
        self.s.Debug("Drag Move Event")
        if event.mimeData().hasFormat("application/flowchart-data"):
            event.accept()
        else:
            event.ignore()

    def drop_event(self, event):
        #print "Drop Event: %s" % str(event)
        #position = self.fd.position()
        view = self.scene.get_view()
        position = view.mapToScene(event.pos())
        #position = QPoint(0, 0)
        self.s.Debug("VC: drop_event()")
        if event.mimeData().hasFormat("application/flowchart-data"):
            data = event.mimeData().data("application/flowchart-data")
            #position = self.fd.position()

            #print "Data: %s" % str(data)
            d = json.loads(str(data))
            if event.dropAction() == Qt.MoveAction:
                self.s.Debug("Moving Slave")
                if "type" in d.keys():
                    self.s.Debug("\tSlave type: %s" % d["type"])
                    if d["type"] == "peripheral_slave":
                        pb = self.boxes["peripheral_bus"]
                        self.s.Debug("\tMoving within peripheral bus")
                        index = pb.find_index_from_position(position)
                        self.move_slave(bus=pb, slave_name = d["name"], to_index = index)
                    else:
                        self.s.Debug("\tMoving within memory bus")
                        mb = self.boxes["memory_bus"]
                        index = mb.find_index_from_position(position)
                        self.move_slave(bus=mb, slave_name = d["name"], to_index = index)
            else:
                if "type" in d.keys():
                    self.s.Debug("\ttype: %s" % d["type"])
                    if d["type"] == "memory_slave" or d["type"] == "peripheral_slave":

                        if d["type"] == "peripheral_slave":
                            self.s.Debug("\tSearching peripheral bus")
                            pb = self.boxes["peripheral_bus"]
                            index = pb.find_index_from_position(position)
                            name = self.model.get_unique_slave_name(d["data"], "peripheral_bus")
                            self.model.add_peripheral_slave(name, module_tags = d["data"], index = index)
                            #self.add_slave(d, index)

                        else:
                            mb = self.boxes["memory_bus"]
                            index = mb.find_index_from_position(position)
                            name = self.model.get_unique_slave_name(d["data"], "memory_bus")
                            #self.add_slave(d, index)
                            self.model.add_memory_slave(name, module_tags = d["data"], index = index)
            event.accept()
        else:
            event.ignore()
        self.refresh_slaves()
        self.refresh_constraint_editor()

    def move_slave(self, bus, slave_name, to_index):
        self.s.Debug("VC: Moving Slave")
        from_index = bus.get_slave_index(slave_name)
        #print "bus type: %s" % bus.get_bus_type()
        nslaves = 0
        slave_type = None
        if bus.get_bus_type() == "peripheral_bus":
            slave_type = SlaveType.PERIPHERAL
        else:
            slave_type = SlaveType.MEMORY

        nslaves = self.model.get_number_of_slaves(slave_type)
        #print "nslaves: %d" % nslaves

        if nslaves == 1:
            self.refresh_slaves()
            return
        if from_index == to_index:
            self.refresh_slaves()
            return


        try:
            self.model.move_slave(slave_name = slave_name,
                                  from_slave_type = slave_type,
                                  from_slave_index = from_index,
                                  to_slave_type = slave_type,
                                  to_slave_index = to_index)

        except ibuilder_error.SlaveError, err:
            pass

        self.refresh_slaves()
        self.refresh_constraint_editor()

    def remove_slave(self, bus, index):
        self.s.Debug("VC: Remove slave")
        slave_type = None
        if bus == "peripheral_bus":
            slave_type = SlaveType.PERIPHERAL
        else:
            slave_type = SlaveType.MEMORY
        self.model.remove_slave(slave_type, index)
        self.refresh_slaves()
        self.refresh_constraint_editor()

    def get_slave_tags(self, bus_name, slave_name):
        slave_type = None
        bus = None
        index = None

        if bus_name == "Peripherals":
            slave_type = SlaveType.PERIPHERAL
            bus = self.boxes["peripheral_bus"]
        else:
            slave_type = SlaveType.MEMORY
            bus = self.boxes["memory_bus"]

        uname = self.model.get_unique_from_module_name(slave_name)
        tags = self.model.get_node_module_tags(uname)
        #print "tags: %s" % str(tags)

        #index = bus.get_slave_index(slave_name)
        #slave = bus.get_slave(slave_name)
        #module_name = self.model.get_slave_name(slave_type, index)
        #print "module name: %s" % module_name
        #slave = bus.get_slave_from_index(index)
        #print "slave: %s" % slave
        return tags

    def bus_refresh_constraint_editor(self, name = None):
        self.dbg = False
        if self.dbg: print "Wishbone Specific Constraint editor refresh"
        if name is not None:
            return

        #Not View Only Mode
        if self.dbg: print "Display all modules"
        pcount = self.model.get_number_of_peripheral_slaves()
        mcount = self.model.get_number_of_memory_slaves()

        for i in range(pcount):
            name = self.model.get_slave_name(SlaveType.PERIPHERAL, i)
            ports = copy.deepcopy(self.model.get_slave_ports(SlaveType.PERIPHERAL, i))
            bindings = self.model.get_slave_bindings(SlaveType.PERIPHERAL, i)
            signals = ports.keys()
            bound_count = 0
            #used to keep a copy of the indexes that are bound, this will be used in the constraints view
            #to tell the user that some of a bus is being used
            used_indexes = []
            #Add connected peripheral signals to the bottom view
            for key in bindings:
                if not bindings[key]["range"]:
                    self.constraint_editor.add_connection(color = PS_COLOR,
                                                          module_name = name,
                                                          port = key,
                                                          direction = bindings[key]["direction"],
                                                          pin_name = bindings[key]["loc"])
                else:
                    #Get the indexes of all the ports that are bound
                    used_indexes = []
                    indexes = copy.deepcopy(bindings[key].keys())
                    used_indexes = copy.deepcopy(bindings[key].keys())
                    indexes.remove("range")
                    used_indexes.remove("range")
                    bound_count = 0
                    for i in indexes:
                        bound_count += 1
                        #XXX: This should change to accomodate the tree constraints view
                        self.constraint_editor.add_connection(color = PS_COLOR,
                                                              module_name = name,
                                                              port = key,
                                                              direction = bindings[key][i]["direction"],
                                                              pin_name = bindings[key][i]["loc"],
                                                              index = i)


                for direction in ports:
                    #Subtract out the ports were used so we don't display them to the user
                    signals = ports[direction].keys()
                    for signal in signals:
                        if signal != key:
                            continue
                        if not bindings[key]["range"]:
                            del(ports[direction][signal])
                        else:
                            if bound_count == ports[direction][signal]["size"]:
                                if self.dbg: print "All of the items in the bus are constrained"
                                del(ports[direction][signal])
                            else:
                                if self.dbg: print "%s is not a port of %s" % (key, signal)
                                ports[direction][signal]["used"] = copy.deepcopy(used_indexes)


            #Show the available peripheral ports in the top left
            for direction in ports:
                for signal in ports[direction]:

                    if signal == "clk":
                        continue
                    if signal == "rst":
                        continue
                    if wishbone_utils.is_wishbone_bus_signal(signal):
                        continue

                    #print "key: %s" % signal
                    s = ports[direction][signal]
                    if "used" not in s:
                        s["used"] = []

                    if s["size"] > 1:
                        #print "used: %s" % str(s["used"])
                        rng = (s["max_val"], s["min_val"])
                        self.constraint_editor.add_signal(PS_COLOR,
                                                          name,
                                                          signal,
                                                          rng,
                                                          direction,
                                                          s["used"])
                    
                    else:
                        self.constraint_editor.add_signal(PS_COLOR,
                                                          name,
                                                          signal,
                                                          None,
                                                          direction)


        for i in range(mcount):
            name = self.model.get_slave_name(SlaveType.MEMORY, i)
            ports = copy.deepcopy(self.model.get_slave_ports(SlaveType.MEMORY, i))
            bindings = self.model.get_slave_bindings(SlaveType.MEMORY, i)
            signals = ports.keys()
            #used to keep a copy of the indexes that are bound, this will be used in the constraints view
            #to tell the user that some of a bus is being used
            used_indexes = []
            #Add connected memory signals to the bottom view
            for key in bindings:
                if not bindings[key]["range"]:
                    self.constraint_editor.add_connection(color = MS_COLOR,
                                                          module_name = name,
                                                          port = key,
                                                          direction = bindings[key]["direction"],
                                                          pin_name = bindings[key]["loc"])
                else:
                    #Get the indexes of all the ports that are bound
                    used_indexes = []
                    indexes = copy.deepcopy(bindings[key].keys())
                    used_indexes = copy.deepcopy(bindings[key].keys())
                    indexes.remove("range")
                    used_indexes.remove("range")
                    bound_count = 0
                    for i in indexes:
                        bound_count += 1
                        #XXX: This should change to accomodate the tree constraints view
                        self.constraint_editor.add_connection(color = MS_COLOR,
                                                              module_name = name,
                                                              port = key,
                                                              direction = bindings[key][i]["direction"],
                                                              pin_name = bindings[key][i]["loc"],
                                                              index = i)


                for direction in ports:
                    #Subtract out any of the ports that I used above
                    signals = ports[direction].keys()
                    for signal in signals:
                        if signal != key:
                            continue
                        if not bindings[key]["range"]:
                            del(ports[direction][signal])
                        else:
                            if bound_count == ports[direction][signal]["size"]:
                                if self.dbg: print "All of the items in the bus are constrained"
                                del(ports[direction][signal])
                            else:
                                if self.dbg: print "%s is not a port of %s" % (key, signal)
                                ports[direction][signal]["used"] = copy.deepcopy(used_indexes)


            #Add the Memory Ports to the available signals
            for direction in ports:
                for signal in ports[direction]:

                    if signal == "clk":
                        continue
                    if signal == "rst":
                        continue
                    if wishbone_utils.is_wishbone_bus_signal(signal):
                        continue

                    #print "signal: %s" % signal
                    s = ports[direction][signal]
                    if "used" not in s:
                        s["used"] = []

                    if s["size"] > 1:
                        #print "used: %s" % str(s["used"])
                        rng = (s["max_val"], s["min_val"])
                        self.constraint_editor.add_signal(MS_COLOR,
                                                          name,
                                                          signal,
                                                          rng,
                                                          direction)
                    
                    else:
                        self.constraint_editor.add_signal(MS_COLOR,
                                                          name,
                                                          signal,
                                                          None,
                                                          direction)


        self.dbg = True

    #Arbiter
    def add_arbiter_link(self, arb_master, slave):
        self.add_link(arb_master, slave, lt.arbiter, st.right)

