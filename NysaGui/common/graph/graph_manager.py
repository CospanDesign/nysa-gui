import os
import sys
import copy
import networkx as nx

from nysa.ibuilder.lib.ibuilder_error import SlaveError
from nysa.ibuilder.lib.ibuilder_error import IBuilderError
from nysa.ibuilder.lib import constraint_utils as cu


def enum(*sequential, **named):
    enums = dict(list(zip(sequential, list(range(len(sequential))))), **named)
    return type('Enum', (), enums)

NodeType = enum('HOST_INTERFACE',
                'MASTER',
                'MEMORY_INTERCONNECT',
                'PERIPHERAL_INTERCONNECT',
                'SLAVE')

SlaveType = enum('MEMORY', 'PERIPHERAL')


def get_unique_name(name,
                    node_type,
                    slave_type=SlaveType.PERIPHERAL,
                    slave_index=0):
    if node_type == NodeType.SLAVE:
        unique_name = name + "_" + str(slave_type) + "_" + str(slave_index)
    else:
        unique_name = name + "_" + str(node_type)
    return unique_name


class Node (object):

    name = ""
    unique_name = ""
    node_type = NodeType.SLAVE
    slave_type = SlaveType.PERIPHERAL
    slave_index = 0
    project_tags = {}
    module_tags = {}
    ports = {}
    bindings = {}

    def __init__(self):
        self.name = ""
        self.unique_name = ""
        self.node_type = NodeType.SLAVE
        self.slave_type = SlaveType.PERIPHERAL
        self.slave_index = 0
        self.project_tags = {}
        self.module_tags = {}
        self.bindings = {}
        self.ports = {}

    def copy(self):
        nn = Node()
        nn.name = self.name
        nn.unique_name = self.unique_name
        nn.node_type = self.node_type
        nn.slave_type = self.slave_type
        nn.slave_index = self.slave_index
        nn.project_tags = self.project_tags.copy()
        nn.module_tags = self.module_tags.copy()
        nn.bindings = self.bindings.copy()
        nn.ports = self.ports.copy()
        return nn

class GraphManager:
    def __init__(self):
        """Initialize the controller."""
        self.graph = nx.Graph()

    #Low Level Node Control
    def clear_graph(self):
        """Resets the graph."""
        self.graph = nx.Graph()

    def add_node(self,
                    name,
                    node_type,
                    slave_type = SlaveType.PERIPHERAL,
                    project_tags = {},
                    module_tags = {},
                    bindings = {},
                    ports = {}):
        '''Adds a node to this graph.'''
        node = Node()
        node.name = name
        node.node_type = node_type
        node.slave_type = slave_type
        node.module_tags = module_tags
        node.project_tags = project_tags
        node.bindings = bindings
        node.ports = ports
        #print "add node bind id: " + str(id(node))

        if slave_type == SlaveType.PERIPHERAL:
            s_count = self.get_number_of_peripheral_slaves()
        else:
            s_count = self.get_number_of_memory_slaves()

        node.slave_index = s_count
        node.unique_name = get_unique_name(name, node_type,
                                            slave_type, node.slave_index)

        if node.unique_name in self.graph.node:
            #print "%s is already in graph: %s" % node.unique_name
            pass
        self.graph.add_node(str(node.unique_name))
        self.graph.node[node.unique_name] = node

        return node.unique_name

    def get_node_names(self):
        """Get all names usually for the purpose of iterating through the
        graph."""
        return self.graph.nodes(False)

    def get_nodes_dict(self):
        graph_dict = {}
        graph_list = self.graph.nodes(True)
        for name, item in graph_list:
            graph_dict[name] = item
        return graph_dict

    def get_node(self, name, debug=False):
        """Gets a node by the unique name."""
        g = self.get_nodes_dict()
        if debug:
            print (("%s: node dict: %s" %
              (__file__, str(self.get_nodes_dict()))))
        if g is None:
            raise  IBuilderError("Node with unique name: %s does not exists" %
                  (name))
        #print "G: %s" % str(g)
        #print "Name: %s" % str(name)
        return g[name]

    def connect_nodes(self, node1, node2):
        """Connects two nodes together."""
        #print "Connecting: %s - %s" % (node1, node2)
        self.graph.add_edge(node1, node2)
        self.graph[node1][node2]["name"] = ""

    def set_edge_name(self, node1_name, node2_name, edge_name):
        """Find the edge connected to the two given nodes."""
        self.graph[node1_name][node2_name]["name"] = edge_name

    def get_edge_name(self, node1_name, node2_name):
        return self.graph[node1_name][node2_name]["name"]

    def remove_node(self, name):
        """Removes a node using the unique name to find it."""

        # Since the master and slave are always constant, the only nodes that
        # can be removed are the slaves.

        # Procedure:
        # - Search for the connections between the interconnect and the slave.
        # - Sever the connection.
        # - If the slave has a master for arbitration purposes, sever that
        #   connection.

        self.graph.remove_node(name)

    def get_size(self):
        return len(self.graph)

    def disconnect_nodes(self, node1_name, node2_name):
        """If the two nodes are connected disconnect them."""
        self.graph.remove_edge(node1_name, node2_name)

    def get_number_of_connections(self):
        return self.graph.number_of_edges()

    #Host Interface Control
    def get_host_interface_node(self):
        graph_dict = self.get_nodes_dict()
        for name in graph_dict:
            node = self.get_node(name)
            if node.node_type == NodeType.HOST_INTERFACE:
                return node

    #SLave Control
    def is_slave_connected_to_slave(self, slave):
        for nb_name in self.graph.neighbors(slave):
            nb = self.get_node(nb_name)
            if nb.node_type == NodeType.SLAVE:
                return True
        return False

    def get_connected_slaves(self, slave_master_name):
        slaves = {}
        for nb_name in self.graph.neighbors(slave_master_name):
            nb = self.get_node(nb_name)
            if nb.node_type == NodeType.SLAVE:
                edge_name = self.get_edge_name(slave_master_name, nb_name)
                slaves[edge_name] = nb.unique_name
        return slaves

    def get_number_of_slaves(self, slave_type):
        '''Gets the number of slaves.  Raises a SaveError if there is no
        slave type or the slave type is SlaveType.PERIPHERAl.'''
        if slave_type is None:
            raise SlaveError("Slave type must be specified")

        if slave_type == SlaveType.PERIPHERAL:
            return self.get_number_of_peripheral_slaves()

        return self.get_number_of_memory_slaves()

    def get_number_of_peripheral_slaves(self):
        '''Counts and returns the number of peripheral slaves.'''
        count = 0
        gd = self.get_nodes_dict()
        for name in gd:
            if gd[name].node_type == NodeType.SLAVE and \
              gd[name].slave_type == SlaveType.PERIPHERAL:
                count += 1
        return count

    def get_number_of_memory_slaves(self):
        '''Counts and returns the number of memory slaves.'''
        count = 0
        gd = self.get_nodes_dict()
        for name in gd:
            if gd[name].node_type == NodeType.SLAVE and \
                gd[name].slave_type == SlaveType.MEMORY:
                count += 1
        return count

    def remove_slave(self, slave_type, slave_index, debug = False):
        # Can't remove the SDB so if the index is 0 then don't try.
        if slave_type == SlaveType.PERIPHERAL and slave_index == 0:
            raise SlaveError("SDB cannot be removed")

        count = self.get_number_of_slaves(slave_type)
        if debug: print "count: %d" % count
        if slave_index >= count:
            if slave_type == SlaveType.PERIPHERAL:
                raise SlaveError(
                    "Slave index %d on peripheral bus is out of range" %
                    (slave_index))
            else:
                raise SlaveError(
                    "Slave index %d on memory bus is out of range" %
                    (slave_index))

        # Move the slave to the end so I can remove it.
        if slave_index < count:
            for index in range(slave_index, count - 1):
                self.move_slave(index, index + 1, slave_type, debug = debug)

        slave_name = self.get_slave_name_at(slave_type, count - 1, debug = debug)
        self.graph.remove_node(slave_name)

    def rename_slave(self, slave_type, slave_index, new_name):
        current_name = self.get_slave_name_at(slave_type, slave_index)
        node = self.get_node(current_name)

        unique_name = get_unique_name(new_name,
                                      NodeType.SLAVE,
                                      slave_type,
                                      slave_index)

        node.name = new_name
        node.unique_name = unique_name
        self.graph = nx.relabel_nodes(self.graph, {current_name: unique_name})

    def fix_slave_indexes(self):
        pcount = self.get_number_of_slaves(SlaveType.PERIPHERAL)
        mcount = self.get_number_of_slaves(SlaveType.MEMORY)

        for i in range(pcount):
            name = self.get_slave_name_at(SlaveType.PERIPHERAL, i)
            node = self.get_node(name)
            node.slave_index = i

        for i in range(mcount):
            name = self.get_slave_name_at(SlaveType.MEMORY, i)
            node = self.get_node(name)
            node.slave_index = i

    def get_slave_at(self, slave_type, index, debug=False):
        name = self.get_slave_name_at(slave_type, index, debug)
        return self.get_node(name)

    def get_slave_name_at(self, slave_type, index, debug=False):
        if slave_type is None:
            raise SlaveError("Peripheral or Memory must be specified")

        graph_dict = self.get_nodes_dict()

        for key in graph_dict:
            node = graph_dict[key]
            if node.node_type != NodeType.SLAVE:
                continue

            if node.slave_type != slave_type:
                continue

            if debug:
                print (("node: %s" % node.name))
                print (("node.slave_index: %s" % str(node.slave_index)))
                print (("index: %s" % str(index)))

            if node.slave_index == index:
                if debug:
                    print ("success")
                return key

        if slave_type == SlaveType.PERIPHERAL:
            raise SlaveError(
              "Unable to locate slave %d on peripheral bus" % (index))
        else:
            raise SlaveError(
              "Unable to locate slave %d on memory bus" % (index))

    def move_slave(self, from_index, to_index, slave_type, debug=False):
        if from_index == to_index:
            return

        if slave_type is None:
            raise SlaveError("Slave Type must be specified")

        if slave_type == SlaveType.PERIPHERAL:
            self.move_peripheral_slave(from_index, to_index, debug)
        else:
            self.move_memory_slave(from_index, to_index, debug)

        # TODO Test me.
        self.fix_slave_indexes()

    def move_peripheral_slave(self, from_index, to_index, debug=False):
        """Move the slaves from the from_index to the to index."""
        s_count = self.get_number_of_peripheral_slaves()
        if to_index >= s_count:
            to_index = s_count - 1

        if from_index == to_index:
            return

        if from_index == 0:
            raise SlaveError("Cannot move SDB")
        if to_index == 0:
            raise SlaveError("SDB is the only peripheral slave at index 0")

        graph_dict = self.get_nodes_dict()

        # Find the slave at the from_index.
        from_node = None
        for key in graph_dict:
            if debug:
                print (("Checking: %s" % (graph_dict[key].name)))
            if graph_dict[key].node_type != NodeType.SLAVE or \
                    graph_dict[key].slave_type != SlaveType.PERIPHERAL:
                continue

            if debug:
                print (("\tChecking index: %d" % (graph_dict[key].slave_index)))

            if graph_dict[key].slave_index != from_index:
                continue

            from_node = graph_dict[key]
            break

        if from_node is None:
            raise SlaveError(
                  "Slave with from index %d not found" % (from_index))

        # Find the slave at the to_index.
        to_node = None
        for key in graph_dict:
            if graph_dict[key].node_type != NodeType.SLAVE or \
                  graph_dict[key].slave_type != SlaveType.PERIPHERAL or \
                  graph_dict[key].slave_index != to_index:
                continue
            to_node = graph_dict[key]
            break

        if to_node is None:
            raise SlaveError("Slave with to index %d not found" % (to_index))

        if debug:
            print ("before move:")
            print (("\tslave %s at position %d with name: %s" %
              (from_node.name, from_node.slave_index, from_node.unique_name)))
            print (("\tslave %s at position %d with name: %s" %
                (to_node.name, to_node.slave_index, to_node.unique_name)))

        from_node.slave_index = to_index
        from_unique = get_unique_name(from_node.name,
                                      from_node.node_type,
                                      from_node.slave_type,
                                      from_node.slave_index)

        #mapping = {from_node.unique_name: from_unique}

        if debug:
            print (("from.unique_name: %s" % from_node.unique_name))
            print (("from_unique: %s" % from_unique))

            print ("keys")
            for name in graph_dict:
                print (("key: %s" % name))

        self.graph = nx.relabel_nodes(self.graph,
                                      {from_node.unique_name: from_unique})
        from_node = self.get_node(from_unique)
        from_node.slave_index = to_index
        from_node.unique_name = from_unique

        to_node.slave_index = from_index
        to_unique = get_unique_name(to_node.name,
                                    to_node.node_type,
                                    to_node.slave_type,
                                    to_node.slave_index)
        self.graph = nx.relabel_nodes(self.graph,
                                      {to_node.unique_name: to_unique})
        to_node = self.get_node(to_unique)

        to_node.slave_index = from_index
        to_node.unique_name = to_unique

        if debug:
            print ("after move:")
            print (("\tslave %s at position %d with name: %s" %
                (from_node.name, from_node.slave_index, from_node.unique_name)))
            print (("\tslave %s at position %d with name: %s" %
                (to_node.name, to_node.slave_index, to_node.unique_name)))

            graph_dict = self.get_nodes_dict()
            print ("keys")
            for name in graph_dict:
                print (("key: %s" % name))

    def move_memory_slave(self, from_index, to_index, debug=False):
        """Move the slave from the from_index to the to_index."""
        s_count = self.get_number_of_memory_slaves()
        if to_index >= s_count:
            to_index = s_count - 1

        if from_index == to_index:
            return

        graph_dict = self.get_nodes_dict()

        # Find the slave at the from_index.
        from_node = None
        for key in graph_dict:
            if graph_dict[key].node_type != NodeType.SLAVE or \
                    graph_dict[key].slave_type != SlaveType.MEMORY or \
                    graph_dict[key].slave_index != from_index:
                continue
            from_node = graph_dict[key]
            break

        if from_node is None:
            raise SlaveError("Slave with from index %d not found" %
                            (from_index))

        # Find the slave at the to_index.
        to_node = None
        for key in graph_dict:
            if graph_dict[key].node_type != NodeType.SLAVE or \
                    graph_dict[key].slave_type != SlaveType.MEMORY or \
                    graph_dict[key].slave_index != to_index:
                continue
            to_node = graph_dict[key]
            break

        if to_node is None:
            raise SlaveError("Slave with to index %d not found" % (to_index))

        if debug:
            print ("before move:")
            print (("\tslave %s at position %d with name: %s" %
                (from_node.name, from_node.slave_index, from_node.unique_name)))
            print (("\tslave %s at position %d with name: %s" %
                (to_node.name, to_node.slave_index, to_node.unique_name)))

        from_node.slave_index = to_index
        from_unique = get_unique_name(from_node.name,
                                      from_node.node_type,
                                      from_node.slave_type,
                                      from_node.slave_index)

        #mapping = {from_node.unique_name: from_unique}

        if debug:
            print (("from.unique_name: %s" % from_node.unique_name))
            print (("from_unique: %s" % from_unique))

            print ("keys")
            for name in graph_dict:
                print (("key: %s" % name))

        self.graph = nx.relabel_nodes(self.graph,
                                      {from_node.unique_name: from_unique})
        from_node = self.get_node(from_unique)
        from_node.slave_index = to_index
        from_node.unique_name = from_unique

        to_node.slave_index = from_index
        to_unique = get_unique_name(to_node.name,
                                    to_node.node_type,
                                    to_node.slave_type,
                                    to_node.slave_index)
        self.graph = nx.relabel_nodes(self.graph,
                                      {to_node.unique_name: to_unique})

        to_node = self.get_node(to_unique)
        to_node.slave_index = from_index
        to_node.unique_name = to_unique

        if debug:
            print ("after move:")
            print (("\tslave %s at position %d with name: %s" %
                (from_node.name, from_node.slave_index, from_node.unique_name)))
            print (("\tslave %s at position %d with name: %s" %
                (to_node.name, to_node.slave_index, to_node.unique_name)))

            graph_dict = self.get_nodes_dict()
            print ("keys")
            for name in graph_dict:
                print (("key: %s" % name))

    #Bindings
    def bind_port(self, name, port_name, loc, index = None, debug=False):
        node = self.get_node(name)
        ports = self.get_node_ports(name)
        #ports = copy.deepcopy(node.ports)
        bindings = self.get_node_bindings(name)

        #print "ports: %s" % str(ports)

        ports = cu.expand_ports(ports)
        ports = cu.get_only_signal_ports(ports)
        port = ports[port_name]
        if port_name not in bindings.keys():
            bindings[port_name] = {}
            
        pdict = bindings[port_name]

        if "range" not in pdict:
            pdict["range"] = port["range"]

        if pdict["range"]:
            #print "port: %s" % str(port)
            if index not in pdict.keys():
                pdict[index] = {}
            pdict[index]["direction"] = port[index]["direction"]
            pdict[index]["loc"] = loc

        else:
            pdict["direction"] = port["direction"]
            pdict["loc"] = loc

    def unbind_port(self, name, port_name, index = None):
        bindings = self.get_node_bindings(name)
        #print "unbind_port"
        #print "\tport name: %s" % port_name
        if port_name not in bindings:
            raise SlaveError(
              "port %s is not in the binding dictionary for node %s"
              % (port_name, name))
        if index is not None:
            #print "\tindex type: %s : %d" % (str(type(index)), index)
            #print "\tindex: %s" % str(index)

            port = bindings[port_name]
            #print "\tport: %s" % str(port)
            if index in port.keys():
                #print "\tport in index"

                if len(port.keys()) == 1:
                    #Only "Range is left
                    #print "\tRange of port is 1!"
                    del(bindings[port_name])
                else:
                    #print "\tRemoving only one item in the port"
                    #del(port[index])
                    #bindings[port_name] = port
                    try:
                        del(bindings[port_name][index])
                        #print "\tCommitting node binding for port: %s" % str(bindings[port_name])
                    except KeyError:
                        raise SlaveError(
                            "port %s:%d is not in the binding dictionery for node %s"
                            % (port_name, index, name))
        else:
            #print "\tdeleting port: %s" % str(port_name)
            del(bindings[port_name])

        self.set_node_bindings(name, bindings)
        b = self.get_node_bindings(name)
        #print "\tbindings: %s" % str(b)

    def set_config_bindings(self, name, bindings):
        node = self.get_node(name)
        node.bindings = bindings
        #for p in bindings:
        #    node.bindings[p] = {}
        #    node.bindings[p]["loc"] = bindings[p]["loc"]
        #    node.bindings[p]["direction"] = bindings[p]["direction"]

    #Graph Node Properties
    def set_node_bindings(self, name, bindings):
        self.get_node(name).bindings = bindings

    def get_node_bindings(self, name):
        return self.get_node(name).bindings

    def set_node_project_tags(self, name, project_tags, debug=False):
        self.get_node(name).project_tags = project_tags

    def get_node_project_tags(self, name):
        return self.get_node(name).project_tags

    def set_node_module_tags(self, name, module_tags):
        self.get_node(name).module_tags = module_tags

    def get_node_module_tags(self, name):
        return self.get_node(name).module_tags

    def update_node_ports(self, name):
        node = self.get_node(name)
        module_tags = node.module_tags
        #for n in self.graph.nodes():
        #    print "Node: %s" % n
        #print "update_node_ports: name: %s" % str(name)
        #print "hi node object: %s" % str(node)
        #print "tags: %s" % str(module_tags)

        if len(module_tags) == 0:
            self.get_node(name)
            node.ports = {}
            return

        #ports = cu.expand_ports(module_tags["ports"])
        ports = module_tags["ports"]
        #print "ports: %s" % str(ports)
        self.get_node(name).ports = ports
        #print "hi ports: %s" % str(self.get_node(name).ports)

    def get_node_ports(self, name):
        return self.get_node(name).ports

    def get_node_display_name(self, uname):
        return self.get_node(uname).name

#  def bind_pin_to_port(self, name, port, loc, debug = False):
#    """
#    binds the specific port to a loc
#    """
#    g = self.get_nodes_dict()
#    if debug:
#      print "Dictionary: " + str(g[name].project_tags["ports"][port])
#    node = self.get_node(name)
#    g[name].project_tags["ports"][port]["port"] = loc


