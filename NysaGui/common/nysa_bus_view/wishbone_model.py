#!/usr/bin/env python

#Distributed under the MIT licesnse.
#Copyright (c) 2013 Cospan Design (dave.mccoy@cospandesign.com)

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




import os
import sys
import json
import copy

from nysa.ibuilder.lib import ibuilder
from nysa.ibuilder.lib import utils
from nysa.ibuilder.lib import verilog_utils as vutils
from nysa.ibuilder.lib import constraint_utils as cu

from nysa.ibuilder.lib.ibuilder_error import SlaveError
from nysa.ibuilder.lib.ibuilder_error import ModuleNotFound

from NysaGui.common.graph.gui_error import WishboneModelError
from NysaGui.common.graph import graph_manager as gm

from NysaGui.common.graph.graph_manager import GraphManager
from NysaGui.common.graph.graph_manager import SlaveType
from NysaGui.common.graph.graph_manager import NodeType
from NysaGui.common.graph.graph_manager import get_unique_name


HOST_INTERFACE     = get_unique_name("Host Interface",
                                            NodeType.HOST_INTERFACE)
MASTER             = get_unique_name("Master", NodeType.MASTER)
MEMORY_BUS         = get_unique_name("Memory", NodeType.MEMORY_INTERCONNECT)
PERIPHERAL_BUS     = get_unique_name("Peripherals",
                                            NodeType.PERIPHERAL_INTERCONNECT)
DRT                = get_unique_name("DRT",
                                            NodeType.SLAVE,
                                            SlaveType.PERIPHERAL,
                                            slave_index=0)



class WishboneModel():
#Good
    def __init__(self, config_dict):
        self.paths = utils.get_local_verilog_paths()
        self.gm = GraphManager()
        self.bus_type = "wishbone"
        self.tags = {}
        self.config_dict = {}
        self.config_dict["PROJECT_NAME"] = "project"
        self.config_dict["TEMPLATE"] = config_dict["TEMPLATE"]
        self.config_dict["INTERFACE"] = {}
        self.config_dict["SLAVES"] = {}
        self.config_dict["MEMORY"] = {}
        self.config_dict["board"] = config_dict["board"]

        self.load_config_dict(config_dict)
        self.initialize_graph()

    def load_config_dict(self, config_dict):
        self.config_dict = config_dict
        self.build_tool = {}
        #self.board_dict = config_dict["board"]

    def get_config_dict(self):
        return self.config_dict

    def initialize_graph(self, debug=False):
        """Initializes the graph and project tags."""
        # Clear any previous data.
        self.gm.clear_graph()

        # Set the bus type.
        if self.config_dict["TEMPLATE"] == "wishbone_template.json":
            self.set_bus_type("wishbone")
        elif self.config_dict["TEMPLATE"] == "axi_template.json":
            self.set_bus_type("axi")
        else:
            raise WishboneModelError("Template is not specified")

        # Add the nodes that are always present.
        self.gm.add_node("Host Interface", NodeType.HOST_INTERFACE)
        self.gm.add_node("Master", NodeType.MASTER)
        self.gm.add_node("Memory", NodeType.MEMORY_INTERCONNECT)
        self.gm.add_node("Peripherals", NodeType.PERIPHERAL_INTERCONNECT)
        self.add_slave("DRT", SlaveType.PERIPHERAL, slave_index=0)

        # Attach all the appropriate nodes.
        self.gm.connect_nodes(HOST_INTERFACE, MASTER)
        self.gm.connect_nodes(MASTER, MEMORY_BUS)
        self.gm.connect_nodes(MASTER, PERIPHERAL_BUS)
        self.gm.connect_nodes(PERIPHERAL_BUS, DRT)

        # Get module data for the DRT.
        # Attempt to load data from the tags.
        #print "Config Dict: %s" % str(self.config_dict)
        if "SLAVES" in self.config_dict:
            for slave_name in self.config_dict["SLAVES"]:
                #Get the slave tags for this project
                slave_project_tags = self.config_dict["SLAVES"][slave_name]
                module_tags = {}
                #Check to see if there is a file for this slave
                if "filename" in slave_project_tags:
                    filename = slave_project_tags["filename"]
                    try:
                        filepath = utils.find_rtl_file_location(filename, self.paths)
                        module_tags = vutils.get_module_tags(filepath)
                    except IOError as ex:
                        #File not found, there is no associated tags with this
                        print "File: %s not found, passing in an empty module" % filename

                uname = self.add_slave(slave_name,
                                       SlaveType.PERIPHERAL,
                                       module_tags = module_tags,
                                       slave_project_tags = slave_project_tags)

        # Load all the memory slaves.
        if "MEMORY" in self.config_dict:
            for slave_name in self.config_dict["MEMORY"]:
                #Get the slave tags for thir project
                slave_project_tags = self.config_dict["MEMORY"][slave_name]
                module_tags = {}
                #Check to see if there is a file for this slave
                if "filename" in slave_project_tags:
                    filename = slave_project_tags["filename"]
                    try:
                        filepath = utils.find_rtl_file_location(filename, self.paths)
                        module_tags = vutils.get_module_tags(filepath)
                    except IOError as ex:
                        #File not found, there is no verilog core associated with this slave on this machine
                        print "File: %s not found, no verilog core associated with this module" % filename

                uname = self.add_slave(slave_name,
                                        SlaveType.MEMORY,
                                        module_tags = module_tags,
                                        slave_project_tags = slave_project_tags)

        # Check if there is a host interface defined.
        if "INTERFACE" in self.config_dict:
            self.setup_host_interface()

        if debug:
            print ("Finish Initialize graph")

    def get_number_of_slaves(self, slave_type):
        if slave_type is None:
            raise SlaveError("slave type was not specified")

        if slave_type == SlaveType.PERIPHERAL:
            return self.get_number_of_peripheral_slaves()

        return self.get_number_of_memory_slaves()

    def get_number_of_memory_slaves(self):
        return self.gm.get_number_of_memory_slaves()

    def get_number_of_peripheral_slaves(self):
        return self.gm.get_number_of_peripheral_slaves()

    def set_board_name(self, board_name):
        self.config_dict["board"] = board_name

    def get_board_name(self):
        if "board" in list(self.config_dict.keys()):
            return self.config_dict["board"]
        return "undefined"

    def set_bus_type(self, bus_type):
        """Set the bus type to Wishbone or Axie."""
        self.bus_type = bus_type

    def get_bus_type(self):
        return self.bus_type

    def get_host_interface_name(self):
        hi = self.gm.get_node(HOST_INTERFACE)
        return "Host Interface"

    def get_constraint_filenames(self):
        board_name = self.config_dict["board"]
        pt = self.config_dict
        if "constraint_files" not in list(pt.keys()):
            pt["constraint_files"] = []

        cfiles = utils.get_constraint_filenames(board_name, debug = True)
        for cf in pt["constraint_files"]:
            cfiles.append(cf)
        return cfiles

    def get_unique_from_module_name(self, module_name):
        """Return the unique name associated with the module_name"""
        if module_name == "Host Interface":
            return self.get_host_interface_name()
        pcount = self.get_number_of_peripheral_slaves()
        for i in range(pcount):
            name = self.get_slave_name(SlaveType.PERIPHERAL, i)
            if module_name == name:
                return get_unique_name(name, NodeType.SLAVE, SlaveType.PERIPHERAL, i)

        mcount = self.get_number_of_memory_slaves()
        for i in range(mcount):
            name = self.get_slave_name(SlaveType.MEMORY, i)
            if module_name == name:
                return get_unique_name(name, NodeType.SLAVE, SlaveType.MEMORY, i)

        raise SlaveError("Module with name %s not found" % module_name)

    #XXX: Work through
    def commit_project_to_tags(self, debug=False):
        """Apply the slave tags to the project tags."""
        # Get all the slaves.
        p_count = self.get_number_of_slaves(SlaveType.PERIPHERAL)
        m_count = self.get_number_of_slaves(SlaveType.MEMORY)
        self.config_dict["SLAVES"] = {}
        self.config_dict["MEMORY"] = {}

        self.gm.set_project_tags(HOST_INTERFACE, cu.expand_user_constraints(self.config_dict["INTERFACE"]))

        for i in range(0, p_count):
            #print "apply slave tags to project: %d:" % i
            sc_slave = self.gm.get_slave_at(SlaveType.PERIPHERAL, i)
            uname = sc_slave.unique_name
            name = sc_slave.name
            if debug:
                print (("name: %s" % str(name)))
            #if debug:
            #    print (("Projct tags: %s" % str(self.config_dict)))
            if name == "DRT":
                continue
            if name not in list(self.config_dict["SLAVES"].keys()):
                self.config_dict["SLAVES"][name] = {}

            pt_slave = self.config_dict["SLAVES"][name]

            # Overwrite the current arbitor dictionary.
            if "BUS" in list(pt_slave.keys()):
                pt_slave["BUS"] = {}

            if "arbitor_masters" in list(sc_slave.project_tags.keys()):
                ams = sc_slave.project_tags["arbitor_masters"]
                if len(ams) > 0:
                    # Add the BUS keyword to the arbitor master.
                    pt_slave["BUS"] = {}
                    # Add all the items from the sc version.
                    for a in ams:
                        if debug:
                            print (("arbitor name: %s" % a))
                        arb_slave = self.get_connected_arbitor_slave(uname, a)

                        arb_name = self.gm.get_node(arb_slave).name
                        if arb_slave is not None:
                            pt_slave["BUS"][a] = arb_name

        # Memory BUS
        for i in range(0, m_count):
            sc_slave = self.gm.get_slave_at(SlaveType.MEMORY, i)
            uname = sc_slave.unique_name
            name = sc_slave.name
            if debug:
                print (("name: %s" % str(name)))
            if name not in list(self.config_dict["MEMORY"].keys()):
                self.config_dict["MEMORY"][name] = {}

            pt_slave = self.config_dict["MEMORY"][name]

            # Overwrite the current arbitor dictionary.
            if "BUS" in list(pt_slave.keys()):
                pt_slave["BUS"] = {}

            if "arbitor_masters" in list(sc_slave.project_tags.keys()):
                ams = sc_slave.project_tags["arbitor_masters"]
                if len(ams) > 0:
                    # Add the BUS keyword to the arbitor master.
                    pt_slave["BUS"] = {}
                    # Add all the items from the sc version.
                    for a in list(ams):
                        if debug:
                            print (("arbitor name: %s" % a))
                        arb_slave = self.get_connected_arbitor_slave(uname, a)

                        arb_name = self.gm.get_node(arb_slave).name
                        if arb_slave is not None:
                            pt_slave["BUS"][a] = arb_name
            module = sc_slave.project_tags["module"]

    def get_graph_manager(self):
        '''Returns the graph manager.'''
        raise Exception("BAD!")
        return self.gm

    #Arbitor Control
    def is_arb_master_connected(self, slave_name, arb_host, debug=False):
        slaves = self.gm.get_connected_slaves(slave_name)
        for key in slaves:
            #print "key: %s" % key
            edge_name = self.gm.get_edge_name(slave_name, slaves[key])
            if (arb_host == edge_name):
                return True
        return False

    def add_arbitor_by_name(self, host_name, arbitor_name, slave_name):
        tags = self.gm.get_project_tags(host_name)
        if arbitor_name not in tags["arbitor_masters"]:
            raise WishboneModelError("%s is not an arbitor of %s" %
                                    (arbitor_name, host_name))

        self.gm.connect_nodes(host_name, slave_name)
        self.gm.set_edge_name(host_name, slave_name, arbitor_name)

    def add_arbitor(self, host_type, host_index,
                         arbitor_name, slave_type, slave_index):
        """Adds an arbitor and attaches it between the host and the slave."""
        h_name = self.gm.get_slave_name_at(host_type, host_index)
        s_name = self.gm.get_slave_name_at(slave_type, slave_index)
        self.add_arbitor_by_name(h_name, arbitor_name, s_name)

    def get_connected_arbitor_slave(self, host_name, arbitor_name):
        tags = self.gm.get_project_tags(host_name)
        if arbitor_name not in tags["arbitor_masters"]:
            SlaveError("This slave has no arbitor masters")

        slaves = self.gm.get_connected_slaves(host_name)
        for arb_name in slaves:
            slave = slaves[arb_name]
            edge_name = self.gm.get_edge_name(host_name, slave)
            if edge_name == arbitor_name:
                return slave
        return None

    def get_connected_arbitor_name(self, host_type, host_index,
                                      slave_type, slave_index):
        h_name = self.gm.get_slave_name_at(host_type, host_index)
        s_name = self.gm.get_slave_name_at(slave_type, slave_index)

        tags = self.gm.get_project_tags(h_name)
        for arb_name in tags["arbitor_masters"]:
            slave_name = self.get_connected_arbitor_slave(h_name, arb_name)
            if slave_name == s_name:
                return arb_name

        raise WishboneModelError(
            "host: %s is not connected to %s" % (h_name, s_name))

    def remove_arbitor_by_arb_master(self, host_name, arb_name):
        slave_name = self.get_connected_arbitor_slave(host_name, arb_name)
        self.remove_arbitor_by_name(host_name, slave_name)

    def remove_arbitor_by_name(self, host_name, slave_name):
        self.gm.disconnect_nodes(host_name, slave_name)

    def remove_arbitor(self, host_type, host_index, slave_type, slave_index):
        """Finds and removes the arbitor from the host."""
        h_name = self.gm.get_slave_name_at(host_type, host_index)
        s_name = self.gm.get_slave_name_at(slave_type, slave_index)
        self.remove_arbitor_by_name(h_name, s_name)

    def is_active_arbitor_host(self, host_type, host_index):
        h_name = self.gm.get_slave_name_at(host_type, host_index)
        tags = self.gm.get_project_tags(h_name)
        if h_name not in tags["arbitor_masters"]:
            if len(tags["arbitor_masters"]) == 0:
                return False

        if not self.gm.is_slave_connected_to_slave(h_name):
            return False

        return True

    def get_arbitor_dict(self, host_type, host_index):
        if not self.is_active_arbitor_host(host_type, host_index):
            return {}

        h_name = self.gm.get_slave_name_at(host_type, host_index)
        return self.gm.get_connected_slaves(h_name)

    #Host Interface
    def setup_host_interface(self):
        #Host interface is always present, if there is a user configuration
        #Associated with it, set all the appropriate values
        #print "setup host interface: %s" % (self.config_dict["PROJECT_NAME"])
        if "INTERFACE" not in self.config_dict:
            print "Interface is not in project tags"
            return
        project_tags = self.config_dict["INTERFACE"]
        self.set_node_project_tags(HOST_INTERFACE, project_tags)

        module_tags = {}

        if "filename" in project_tags:
            filename = project_tags["filename"]
            try:
                filepath = utils.find_rtl_file_location(filename, self.paths)
                module_tags = vutils.get_module_tags(filepath)
            except:
                print "%s: Could not  find Host Interface for file: %s" % (__file__, filename)

        self.set_node_module_tags(HOST_INTERFACE, module_tags)
        self.update_node_ports(HOST_INTERFACE)
        if "bind" in project_tags:
            self.set_node_bindings(HOST_INTERFACE, cu.expand_user_constraints(project_tags["bind"]))
        #self.set_node_bindings(HOST_INTERFACE, project_tags["bind"])

    def get_host_interface_ports(self):
        return self.get_node_ports(HOST_INTERFACE)

    #Slave Control
    def add_drt(self):
        DRT_NAME = "DRT"
        slave = None
        try:
            slave = self.gm.get_slave_at(SlaveType.PERIPHERAL, 0)
        except SlaveError:
            pass

        if slave is not None:
            #print "%s: add_drt: name: %s" % (__file__, slave.name)
            if slave.name == DRT_NAME:
                #print "%s: DRT Already in Graph Manager" % (__file__)
                return
        s_count = self.gm.get_number_of_peripheral_slaves()
        uname = self.gm.add_node(   DRT_NAME,
                                    NodeType.SLAVE,
                                    SlaveType.PERIPHERAL)

        slave = self.gm.get_node(uname)
        self.gm.move_peripheral_slave(slave.slave_index, 0)

    def add_peripheral_slave(self, name, module_tags = {}, project_tags = None, index = -1):
        self.add_slave(name, SlaveType.PERIPHERAL, module_tags, project_tags, index)

    def add_memory_slave(self, name, module_tags = {}, project_tags = None, index = -1):
        self.add_slave(name, SlaveType.MEMORY, module_tags, project_tags, index)

    def add_slave(self, name, slave_type, module_tags = {}, slave_project_tags = None, slave_index=-1):
        """Adds a slave to the specified bus at the specified index."""
        # Check if the slave_index makes sense.  If slave index s -1 then add it
        # to the next available location
        if name == "DRT":
            return self.add_drt()

        if slave_project_tags is None:
            slave_project_tags = {}
            slave_project_tags["filename"] = utils.find_module_filename(module_tags["module"])
            slave_project_tags["bind"] = {}

        slave = None

        module_ports = {}
        if "ports" in module_tags:
            #module_ports = cu.expand_ports(module_tags["ports"])
            module_ports = module_tags["ports"]

        bindings = {}
        if "bind" in slave_project_tags:
            bindings = cu.expand_user_constraints(slave_project_tags["bind"])

        #Check to see if the project overrides the project_tags
        self.gm.add_node( name,
                          NodeType.SLAVE,
                          slave_type,
                          project_tags = slave_project_tags,
                          module_tags = module_tags,
                          ports = module_ports,
                          bindings = bindings)

        s_count = self.gm.get_number_of_slaves(slave_type)
        #If the user didn't specify the slave index put it at the end
        if slave_index == -1:
            slave_index = s_count

        else:  # Add the slave wherever.
            if slave_type == SlaveType.PERIPHERAL:
                if slave_index == 0 and name != "DRT":
                    raise gm.SlaveError("Only the DRT can be at position 0")
                s_count = self.gm.get_number_of_peripheral_slaves()
                uname = get_unique_name(name,
                                             NodeType.SLAVE,
                                             slave_type,
                                             s_count - 1)
                slave = self.gm.get_node(uname)
                if slave_index < s_count - 1:
                    self.gm.move_peripheral_slave(slave.slave_index,
                                                  slave_index)
            elif slave_type == SlaveType.MEMORY:
                s_count = self.gm.get_number_of_memory_slaves()
                uname = get_unique_name(name,
                                             NodeType.SLAVE,
                                             slave_type,
                                             s_count - 1)
                slave = self.gm.get_node(uname)
                if slave_index < s_count - 1:
                    self.gm.move_slave(slave.slave_index,
                                       slave_index,
                                       SlaveType.MEMORY)

    def move_slave(self,
                   slave_name=None,
                   from_slave_type=SlaveType.PERIPHERAL,
                   from_slave_index=0,
                   to_slave_type=SlaveType.PERIPHERAL,
                   to_slave_index=0):
        """Move slave from one place to another, the slave can be moved from one
        bus to another and the index position can be moved."""
        #print "from slave index: %d" % from_slave_index
        #print "to slave index: %d" % to_slave_index
        if from_slave_type == SlaveType.PERIPHERAL and from_slave_index == 0:
            return

        if to_slave_type == SlaveType.PERIPHERAL and to_slave_index == 0:
            to_slave_index = 1

        if slave_name is None:
            gm.SlaveError("a slave name must be specified")

        if from_slave_type == to_slave_type:
            # Simple move call.
            self.gm.move_slave(from_slave_index,
                               to_slave_index,
                               from_slave_type)
            return

    def remove_slave(self, slave_type=SlaveType.PERIPHERAL, slave_index=0):
        """Removes slave from specified index."""
        #Check if there are any bindings to remove
        name = self.get_slave_name(slave_type, slave_index)
        if slave_type == SlaveType.PERIPHERAL:
            del(self.config_dict["SLAVES"][name])
        else:
            del(self.config_dict["MEMORY"][name])
        bindings = self.get_slave_bindings(slave_type, slave_index)
        uname = get_unique_name(name, NodeType.SLAVE, slave_type, slave_index)
        bnames = bindings.keys()
        for bname in bnames:
            bind = bindings[bname]

            if bind["range"]:
                indexes = bind.keys()
                indexes.remove("range")
                for index in indexes:
                    self.gm.unbind_port(uname, bname, index)

                break
            else:
                self.gm.unbind_port(uname, bname)
                break
        self.gm.remove_slave(slave_type, slave_index)
        return

    def get_slave_ports(self, slave_type, slave_index):
        slave_name = self.get_slave_name(slave_type, slave_index)
        uname = get_unique_name(slave_name, NodeType.SLAVE, slave_type,
                                     slave_index)
        return self.get_node_ports(uname)

    def get_slave_name(self, slave_type, slave_index):
        s_name = self.gm.get_slave_name_at(slave_type, slave_index)
        slave = self.gm.get_node(s_name)
        return slave.name

    def get_slave_name_by_unique(self, slave_name):
        node = self.gm.get_node(slave_name)
        return node.name

    #Bindings
    def set_node_bindings(self, node_name, bindings):
        self.gm.set_node_bindings(node_name, bindings)

    def bind_port(self, node_name, port_name, pin_name, index=None):
        """Add a binding between the port and the pin."""
        un = self.get_unique_from_module_name(node_name)
        self.gm.bind_port(un, port_name, pin_name, index)
        return

    def unbind_port(self, node_name, port_name, index=None):
        """Remove a binding with the port name."""
        if node_name == "Host Interface":
            node_name = HOST_INTERFACE
        #uname = self.get_unique_from_module_name(node_name)
        self.gm.unbind_port(node_name, port_name, index)

    def unbind_all(self, debug=False):
        if debug:
            print ("unbind all")
        mbd = self.get_consolodated_master_bind_dict()
        if debug:
            print (("Master Bind Dict: %s" % str(mbd)))
        node_names = self.gm.get_node_names()
        for nn in node_names:
            nb = copy.deepcopy(self.gm.get_node_bindings(nn))
            for b in nb:
                if debug:
                    print (("Unbindig %s" % b))
                self.gm.unbind_port(nn, b)

    def get_global_bindings(self):
        if "bind" not in self.config_dict:
            self.config_dict["bind"] = {}
        return self.config_dict["bind"]

    def get_available_internal_bind_signals(self):
        #XXX: Get all internal signals from the generated top document
        return []

    def get_possible_internal_bind_signals(self, name):
        #XXX: Get all internal signals from the generated top document that can
        #connect to available signal
        return []
        
    def get_internal_bindings(self):
        if "internal_bind" not in self.config_dict:
            self.config_dict["internal_bind"] = {}

        return self.config_dict["internal_bind"]

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
        self.config_dict["internal_bind"][to_signal] = from_signal

    def unbind_internal_signal(self, to_signal):
        """ unbind the signals that are connected to to_signal

        Args:
            to_signal (str): signal to detach

        Return:
            Nothing

        Raises:
            Nothing
        """
        #Change all strings to standard python string
        to_signal = str(to_signal)
        if to_signal in self.config_dict["internal_bind"]:
            del(self.config_dict["internal_bind"][to_signal])
        
    def get_consolodated_master_bind_dict(self):
        """Combine the dictionary from:
          - project
          - host interface
          - peripheral slaves
          - memory slaves

          The returned dictionary is consolodated in that all the pins are
          not expanded to a unique index, this is good for a project but not
          good for manipulation
          """

        # The dictionary to put the entries in and return.
        bind_dict = {}

        # Get project bindings.
        print "TODO: Need to visualize the board level binds like CLOCK and RESET!"
        #print "config dict: %s" % str(self.config_dict)
        bind = self.config_dict["bind"]
        for k in bind:
            bind_dict[k] = bind[k]

        # Get host interface bindings.
        hib = cu.consolodate_constraints(self.gm.get_node_bindings(HOST_INTERFACE))
        for k, v in list(hib.items()):
            bind_dict[k] = v

        # Get all the peripheral slave bindings.
        p_count = self.get_number_of_slaves(SlaveType.PERIPHERAL)
        for i in range(p_count):
            slave = self.gm.get_slave_at(SlaveType.PERIPHERAL, i)
            pb = cu.consolodate_constraints(
                                self.gm.get_node_bindings(slave.unique_name))
            for key in pb:
                bind_dict[key] = pb[key]

        # Get all the memory slave bindings.
        m_count = self.get_number_of_slaves(SlaveType.MEMORY)
        for i in range(m_count):
            slave = self.gm.get_slave_at(SlaveType.MEMORY, i)
            mb = cu.consolodate_constraints(
                                self.gm.get_node_bindings(slave.unique_name))
            for key in mb:
                bind_dict[key] = mb[key]

        return bind_dict

    def get_expanded_master_bind_dict(self):
        """Create a large dictionary of all the constraints from
            - project
            - host interface
            - peripheral slaves
            - memory slaves
        """
        bind_dict = {}
        bind_dict["project"] = cu.expand_user_constraints(
                                        self.config_dict["bind"])
        bind_dict["host interface"] = self.get_host_interface_bindings()

        #Get Peripheral Slaves
        p_count = self.get_number_of_slaves(SlaveType.PERIPHERAL)
        for i in range(p_count):
            slave = self.gm.get_slave_at(SlaveType.PERIPHERAL, i)
            bind_dict[slave.name] = self.gm.get_node_bindings(slave.unique_name)

        #Get Memory Slaves
        m_count = self.get_number_of_slaves(SlaveType.MEMORY)
        for i in range(m_count):
            slave = self.gm.get_slave_at(SlaveType.MEMORY, i)
            bind_dict[slave.name] = self.gm.get_node_bindings(slave.unique_name)

        return bind_dict

    def get_slave_bindings(self, slave_type, slave_index):
        slave_name = self.get_slave_name(slave_type, slave_index)
        uname = get_unique_name(slave_name,
                                     NodeType.SLAVE,
                                     slave_type,
                                     slave_index)
        return self.gm.get_node_bindings(uname)

    def get_host_interface_bindings(self):
        return self.gm.get_node_bindings(HOST_INTERFACE)

    #Setting Graph Node Properties
    def update_node_bindings_from_project(self, uname):
        project_tags = self.gm.get_project_tags(uname)
        bindings = project_tags["bind"]
        self.gm.set_node_bindings(uname, bindings)

    def get_node_bindings(self, uname):
        return self.gm.get_node_bindings(uname)

    def set_node_project_tags(self, uname, tags):
        self.gm.set_node_project_tags(uname, tags)

    def get_node_project_tags(self, uname):
        return self.gm.get_node_project_tags(uname)

    def set_node_module_tags(self, uname, tags):
        self.gm.set_node_module_tags(uname, tags)

    def get_node_module_tags(self, uname):
        return self.gm.get_node_module_tags(uname)

    def update_node_ports(self, uname):
        self.gm.update_node_ports(uname)

    def get_node_ports(self, uname):
        return self.gm.get_node_ports(uname)

    def _commit_bindings_to_project_tags(self, uname):
        bindings = self.gm.get_node_bindings(uname)
        #bindings = cu.consolodate_constraints(bindings, debug = True)
        bindings = cu.consolodate_constraints(bindings)
        tags = self.get_node_project_tags(uname)
        #print "old tags: "
        #utils.pretty_print_dict(tags)
        tags["bind"] = bindings
        #print "new tags: "
        #utils.pretty_print_dict(tags)
        if self.gm.get_node(uname).node_type == NodeType.HOST_INTERFACE:
            self.config_dict["INTERFACE"] = self.gm.get_node_project_tags(uname)
        elif self.gm.get_node(uname).node_type == NodeType.SLAVE:
            if self.gm.get_node(uname).slave_type == SlaveType.PERIPHERAL:
                self.config_dict["SLAVES"][self.gm.get_node(uname).name] = self.gm.get_node_project_tags(uname)
            else:
                self.config_dict["MEMORY"][self.gm.get_node(uname).name] = self.gm.get_node_project_tags(uname)
            

    def commit_all_project_tags(self):
        #Go through the host interface first
        self._commit_bindings_to_project_tags(HOST_INTERFACE)

        pcount = self.get_number_of_peripheral_slaves()
        for i in range(pcount):
            uname = self.gm.get_slave_name_at(SlaveType.PERIPHERAL, i)
            print "uname: %s" % uname
            #name = self.gm.get_node(uname).name
            #print "name: %s" % self.gm.get_node(uname).name
            '''
            if name not in self.config_dict["SLAVES"]:
                self.config_dict["SLAVES"][name] = {
                        "filename":self.gm.get_node_module_tags(uname)["filename"],
                        "bind":{}
                        }
            '''
            #uname = get_unique_name(name, NodeType.SLAVE, SlaveType.PERIPHERAL, i)
            self._commit_bindings_to_project_tags(uname)

        mcount = self.get_number_of_memory_slaves()
        for i in range(mcount):
            uname = self.gm.get_slave_name_at(SlaveType.MEMORY, i)
            #uname = self.gm.get_slave_name_at(SlaveType.MEMORY, i)
            #uname = get_unique_name(name, NodeType.SLAVE, SlaveType.MEMORY, i)
            self._commit_bindings_to_project_tags(uname)


    def get_unique_slave_name(self, module_tags, bus):
        #print "bus: %s" % str(bus)
        count = 0
        ucount = 0
        bus_type = SlaveType.PERIPHERAL
        if bus == "peripehral_bus":
            count = self.gm.get_number_of_peripheral_slaves()
        else:
            count = self.gm.get_number_of_memory_slaves()
            bus_type = SlaveType.MEMORY

        for i in range(count):
            slave = self.gm.get_slave_at(bus_type, i)
            if "module" in slave.module_tags:
                if module_tags["module"] == slave.module_tags["module"]:
                    ucount += 1
        return "%s_%d" % (module_tags["module"], ucount)

    def set_project_name(self, name):
        self.config_dict["PROJECT_NAME"] = name

    def get_project_name(self):
        return self.config_dict["PROJECT_NAME"]

