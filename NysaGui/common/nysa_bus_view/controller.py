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

import os
import sys
import copy


from PyQt4.QtCore import *
from PyQt4.QtGui import *

p = os.path.join(os.path.dirname(__file__),
                             os.pardir)
p = os.path.abspath(p)
print "%s: Path Append: %s" % (__file__, p)
sys.path.append(p)


from pvg.visual_graph.box import Box

def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)

lt = enum(   "bus",
             "host_interface",
             "arbiter",
             "slave",
             "port",
             "arbiter_master")


st = enum(   "top",
             "bottom",
             "right",
             "left")

from defines import HI_COLOR
from defines import PS_COLOR
from defines import MS_COLOR

from nysa.ibuilder.lib import constraint_utils as cu
from nysa.ibuilder.lib import utils

no_detect_ports = [
    "rst",
    "clk",
    "o_in_address",
    "i_out_address",
    "o_oh_ready",
    "o_in_data_count",
    "o_ih_ready",
    "o_in_command",
    "i_ftdi_suspend_n",
    "o_ih_reset",
    "i_out_status",
    "i_master_ready",
    "i_out_data",
    "i_out_data_count",
    "i_oh_en",
    "io_ftdi_data",
    "o_in_data"
]



def enum(*sequential, **named):
    enums = dict(list(zip(sequential, list(range(len(sequential))))), **named)
    return type('Enum', (), enums)

BoxType = enum('HOST_INTERFACE',
               'MASTER',
               'MEMORY_INTERCONNECT',
               'PERIPHERAL_INTERCONNECT',
               'SLAVE')


class DesignControlError(Exception):
    """
    Errors associated with the Controller

    Error associated with:
        -bus/axi model not configured correclty
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Controller (QObject):

    def __init__(self, model, status):
        self.status = status
        QObject.__init__(self)

        self.model = model
        self.canvas = None
        self.boxes = {}
        self.constraint_editor = None
        """
        Go through view and connect all relavent events
        """

    def set_canvas(self, canvas):
        self.canvas = canvas
        self.canvas.set_controller(self)

    def remove_user_dir(self, user_dir):
        self.model.remove_user_path(user_dir)

    def drag_enter(self, event):
        """
        An item has entered the canvas
        """
        #Check if the item is the correct type
        raise NotImplementedError("This function should be subclassed")

    def drag_move(self, event):
        """
        An item is dragged around the canvas

        Detect if a movement is valid
        """
        #get the type of device (slave/host interface/master)
        """
        This class should be subclassed for bus or Axi because Axi
        can add and remove masters
        """
        raise NotImplementedError("This function should be subclassed")

    def drop_event(self, position, event):
        """
        An item has been dropped
        """
        #Handle an addition/move of a slave
        #Handle an addition/remove of a host interface
        raise NotImplementedError("This function should be subclassed")

    def add_box(self, box_type, color, name, ID, position, rect=QRect()):
        """Add a box to the canvas"""
        scene = self.canvas.scene()
        if box_type == BoxType.SLAVE:
            fn = utils.find_module_filename(name, utils.get_local_verilog_paths())
            fn = utils.find_rtl_file_location(fn, utils.get_local_verilog_paths())

        if self.model is None:
            raise DesignControlError("Bus type is not set up corretly," +
                                     "please select either axi or bus")
        #self.model.add_slave
        return Box(position=position,
                   scene=scene,
                   name=name,
                   color=color,
                   select_func=self.box_select,
                   deselect_func=self.box_deselect,
                   user_data=ID)

    def get_index_from_position(self, position):
        #Check if this is the peripheral bus or the memory slave
        #If this is the peripheral bus then
        return -1

    def remove_box(self, ID):
        """
        Remove the slave from both the visual interface and from the model
        """
        pass

    def valid_box_area(self, ID, rect, position):
        """
        This class should be subclassed

        Description: Analyzes whether the box should be allowed to be dropped
        """
        raise NotImplementedError("This function should be subclassed")

    def zoom_rect(self, rect):
        """
        Zoom to a selected region
        """
        #The user may not be able to actually zoom to a region (it may not be
        #   the correct geometry, how to handle this?

        #Can this be animated :) ??

    def set_config_file(self, config_file):
        if self.model is None:
            raise DesignControlError("Bus type is not set up corretly," +
                                     "please select either axi or bus")
        self.status.Debug( "set the configuration file")
        self.model.load_config_file(config_file)
        self.model.initialize_graph(self)

    def set_board_name(self, board_name):
        self.model.set_board_name(board_name)
        self.model.initialize_graph(self)
        
    def set_default_board_project(self, board_name):
        if self.model is None:
            raise DesignControlError("Bus type is not set up corretly," +
                                     "please select either axi or bus")

        self.model.set_default_board_project(board_name)
        self.model.initialize_graph(self)

    def set_bus(self, bus):
        raise NotImplementedError("This function should be subclassed")

    def get_bus(self):
        return self.bus

    def add_link(self, from_box, to_box, link_type, side):
        from_box.add_connection(to_box, link_type, side)

    def add_slave_link(self, bus, slave):
        self.add_link(bux, slave, lt.bus_bus, st.right)

    def add_host_interface_link(self, hi, m):
        self.add_link(hi, m, lt.host_interface, st.right)

    def add_bus_link(self, m, bus):
        self.add_link(m, bus, lt.bus, st.right)

    def set_project_name(self, name):
        raise NotImplementedError("This function should be subclassed")

    def get_project_name(self):
        raise NotImplementedError("This function should be subclassed")

    def item_is_enabled(self, path):
        #print "VC: Path: %s" % path
        return True

    def connect_signal(self, module_name, signal_name, direction, index, pin_name):
        #print "Connect"
        self.model.set_binding(module_name, signal_name, pin_name, index)

    def disconnect_signal(self, module_name, signal_name, direction, index, pin_name):
        #Remove signal from model
        #print "Controller: Disconnect"
        uname = self.model.get_unique_from_module_name(module_name)
        self.model.unbind_port(uname, signal_name, index)

    def get_model(self):
        return self.model

    def initialize_constraint_editor(self, constraint_editor):
        #print "Initialize constraint editor"
        self.constraint_editor = constraint_editor
        self.constraint_editor.set_connect_callback(self.connect_signal)
        self.constraint_editor.set_disconnect_callback(self.disconnect_signal)
        self.constraint_editor.initialize_view()
        self.refresh_constraint_editor()

    def initialize_configuration_editor(self, configuration_editor):
        self.configuration_editor = configuration_editor
        self.configuration_editor.set_project_name(self.get_project_name())
        self.configuration_editor.populate_board_list(utils.get_board_names())
        self.configuration_editor.set_board(self.model.get_board_name())
        self.configuration_editor.populate_connected_signals(self.model.get_internal_bindings())
        self.configuration_editor.populate_available_signals(self.model.get_available_internal_bind_signals())
        self.configuration_editor.populate_constraints_file_list(self.model.get_constraint_filenames())

    def get_project_location(self):
        return self.model.get_project_location()

    def refresh_constraint_editor(self, name = None):
        #If a name is present just populate connections for that one item
        #   e.g. the host interface, master, etc...
        if self.constraint_editor is None:
            #print "constraint editor is none"
            return

        mbd = self.model.get_consolodated_master_bind_dict()
        self.constraint_editor.clear_all()

        if name is None or name == "Host Interface":
            #for key in mbd:
            #    print "%s: %s" % (key, mbd[key])

            #print "Get bindings for host_interface"
            hib = self.model.get_host_interface_bindings()
            #print "Get ports for host interface"
            hip = copy.deepcopy(self.model.get_host_interface_ports())
            for direction in hip:
                #print "direction: %s" % direction
                #Go through all the signals in this particular direction
                signals = hip[direction].keys()
                for signal in signals:
                    #Remove any of the standard 'reset', 'clock' or wishbone signals
                    if signal in no_detect_ports:
                        #print "Remove: %s" % signal
                        del(hip[direction][signal])
                        continue

                #print "\tsignals: %s" % str(hip[direction].keys())

                #print "hib: %s" % str(hib)

            bound_count = 0
            for key in hib:
                if not hib[key]["range"]:
                    self.constraint_editor.add_connection(color = HI_COLOR,
                                                          module_name = "Host Interface",
                                                          port = key,
                                                          direction = hib[key]["direction"],
                                                          pin_name = hib[key]["loc"])
                else:
                    indexes = copy.deepcopy(hib[key].keys())
                    indexes.remove("range")
                    bound_count = 0
                    for i in indexes:
                        bound_count += 1
                        #n = "%s[%d]" % (key, i)
                        self.constraint_editor.add_connection(color = HI_COLOR,
                                                              module_name = "Host Interface",
                                                              port = key,
                                                              direction = hib[key][i]["direction"],
                                                              pin_name = hib[key][i]["loc"],
                                                              index = i)

                for direction in hip:
                    signals = hip[direction].keys()
                    #Remove signals from ports list
                    if key in signals:
                        if not hib[key]["range"]:
                            #print "remove an item that has only no range: %s" % key
                            del(hip[direction][key])
                        else:
                            #print "Signal: %s" % key
                            #print "Checking if bound count: %d == %d" % (bound_count, ports[key]["size"])
                            if bound_count == ports[key]["size"]:
                                #print "All of the items in the bus are constrained"
                                #signals.remove[key]
                                del(hip[direction][key])
                    else:
                        #print "%s is not a port of %s" % (key, name)
                        pass


            #print "Hports keys: %s" % str(signals)
            for direction in hip:
                for signal in hip[direction].keys():
                    #print "signal: %s: %s" % (signal, str(hip[direction][signal]))
                    if hip[direction][signal]["size"] > 1:
                        rng = (hip[direction][signal]["max_val"], hip[direction][signal]["min_val"])
                        self.constraint_editor.add_signal(HI_COLOR,
                                                          "Host Interface",
                                                          signal,
                                                          rng,
                                                          direction)
                    else:
                        self.constraint_editor.add_signal(HI_COLOR,
                                                          "Host Interface",
                                                          signal,
                                                          None,
                                                          direction)


        if name is None or name != "Host Interface":
            #Call the bus specific interface
            self.bus_refresh_constraint_editor(name)

        #populate the constraint view
        cfiles = self.model.get_constraint_filenames()
        constraints = []
        for f in cfiles:
            constraints.extend(utils.get_net_names(f))

        #print "constraints: %s" % str(constraints)

        #Don't let the user select where the clk and rst are, let the board file do this
        if "clk" in constraints:
            constraints.remove("clk")
        if "rst" in constraints:
            constraints.remove("rst")
        if "rst_n" in constraints:
            constraints.remove("rst_n")

        #Go through all the connected signals and create a list of constraint that are not used
        mbd = self.model.get_expanded_master_bind_dict()
        #print "mbd: %s" % str(mbd)
        #print "constraints: %s" % str(constraints)
        for module in mbd:
            module_dict = mbd[module]
            for signal in module_dict:
                signal_dict = module_dict[signal]

                #print "signal: %s" % str(signal)
                if signal_dict["range"]:
                    #print "check range"
                    ikeys = copy.deepcopy(signal_dict.keys())
                    ikeys.remove("range")
                    for i in ikeys:
                        if signal_dict[i]["loc"] in constraints:
                            #print "Checking: %s" % signal_dict[i]["loc"]
                            constraints.remove(signal_dict[i]["loc"])
                else:
                    if signal_dict["loc"] in constraints:
                        constraints.remove(signal_dict["loc"])

        for c in constraints:
            self.constraint_editor.add_pin(c)

    def bus_refresh_constraint_editor(self, name = None):
        raise NotImplementedError("This function should be subclassed")

    def get_constraint_editor(self):
        return self.constraint_editor

    def connect_signal(self, module_name, signal_name, direction, index, pin_name):
        #print "Connect"
        self.model.bind_port(module_name, signal_name, pin_name, index)
        self.refresh_constraint_editor()

    def disconnect_signal(self, module_name, signal_name, direction, index, pin_name):
        #Remove signal from model
        #print "Controller: Disconnect"
        uname = self.model.get_unique_from_module_name(module_name)
        #print "unbind: %s, index %s" % (str(signal_name), str(index))
        self.model.unbind_port(uname, signal_name, index)
        self.constraint_editor.remove_connection(module_name, signal_name, index)
        self.refresh_constraint_editor()

    def get_config_dict(self):
        return self.model.get_config_dict()

    def get_module_module_tags(self, module_name):
        uname = self.model.get_unique_from_module_name(module_name)
        return self.model.get_module_tags(uname)

    def get_module_project_tags(self, module_name):
        uname = self.model.get_unique_from_module_name(module_name)
        return self.model.get_node_project_tags(uname)

    def unbind_all(self):
        """  unbind all signals in the design

        Args:
            Nothing

        Returns:
            Nothing

        Raises:
            Nothing
        """
        self.model.unbind_all()
        self.refresh_constraint_editor()

    def bind_internal_signal(self, to_signal, from_signal):
        """ bind to_signal to from_signal, this will create a line like this

        assign  to_signal = from_signal

        Note: it is possible that the background utilities will actually barf on
        this, the user has a lot of freedom to connect an arbitrary signal and
        possibly create loops, so if errors do occur during build this may be
        the root

        Args:
            to_signal (str): destination signal
            from_signal (str): source signal

        Returns:
            Nothing

        Raises:
            Nothing
        """
        #Pass this to the model, this is where the config_dict is held
        to_signal = str(to_signal)
        from_signal = str(from_signal)
        self.model.bind_internal_signal(to_signal, from_signal)
        self.initialize_configuration_editor(self.configuration_editor)

    def unbind_internal_signal(self, to_signal):
        """ unbind the signals that are connected to to_signal

        Args:
            to_signal (str): signal to detach

        Return:
            Nothing

        Raises:
            Nothing
        """
        to_signal = str(to_signal)
        #Pass this to the model, this is where the config_dict is held
        self.model.unbind_internal_signal(to_signal)
        self.initialize_configuration_editor(self.configuration_editor)

    def add_constraint_file(self, constraint_fname):
        self.model.add_constraint_file(str(constraint_fname))
        self.initialize_configuration_editor(self.configuration_editor)

    def remove_constraint_file(self, constraint_fname):
        self.model.remove_constraint_file(constraint_fname)
        self.initialize_configuration_editor(self.configuration_editor)

    def add_default_board_constraint(self):
        self.model.add_default_board_constraint()
        self.initialize_configuration_editor(self.configuration_editor)
        self.refresh_constraint_editor()

    def remove_default_board_constraint(self):
        self.model.remove_default_board_constraint()
        self.initialize_configuration_editor(self.configuration_editor)
        self.refresh_constraint_editor()

    def commit_slave_parameters(self, name, param_dict):
        self.model.commit_slave_parameters(name, param_dict)

    '''
    def slave_selected(self, slave_type, slave_name):
        pass

    def slave_deselected(self, slave_type, slave_name):
        pass

    def node_selected(self, node_type, node_name, slave_type = Slave.PERIPHERAL):
        pass

    def node_deselected(self, node_type, node_name, slave_type = Slave.PERIPHERAL):
        pass
    '''
