import sys
import os
import time

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from graphics_scene import GraphicsScene
from graphics_view import GraphicsView

p = os.path.join(os.path.dirname(__file__), 
                 os.pardir,
                 os.pardir,
                 os.pardir,
                 os.pardir,
                 "pvg")

p = os.path.abspath(p)
sys.path.append(p)

from visual_graph.graphics_widget import GraphicsWidget



from wishbone_controller import WishboneController

from defines import *


class VisualizerWidget(QWidget):

    def __init__(self, actions):
        self.actions = actions
        super (VisualizerWidget, self).__init__()
        self.visualizer = VisualizerView(self, actions)
        self.controller = None
        layout = QVBoxLayout()
        layout.addWidget(self.visualizer)
        self.setLayout(layout)

    def update_view(self, config_dict):
        self.config_dict = config_dict
        if config_dict["bus_type"] == "wishbone":
            self.controller = WishboneController(config_dict, self.visualizer.scene)
        else:
            raise NotImplemented("Implement AXI Interface!")

        self.controller.initialize_view()
        self.visualizer.update()

        if self.first:
            #XXX: Hack, How to resize this without manually doing this the first time??
            self.first = False
            m = self.controller.get_model()
            npslaves = m.get_number_of_peripheral_slaves()

            height = (SLAVE_RECT.height() * npslaves + SLAVE_VERTICAL_SPACING)
            width = (SLAVE_RECT.width() +
                    PERIPHERAL_BUS_RECT.width() +
                    MASTER_RECT.width() +
                    HOST_INTERFACE_RECT.width() +
                    (SLAVE_HORIZONTAL_SPACING * 4))
            r = QRectF(0, 0, height, 100)
            self.visualizer.view.fitInView(r, Qt.KeepAspectRatio)

    def sizeHint (self):
        size = QSize()
        size.setWidth(600)
        return size



class VisualizerView(GraphicsWidget):

    def __init__(self, parent, actions):
        self.actions = actions
        self.view = GraphicsView(parent)
        self.scene = GraphicsScene(self.view, self.actions)
        super(VisualizerView, self).__init__(self.view, self.scene)
        self.boxes = {}
        self.show()

    def clear(self):
        #print "Items: %s" % str(self.view.items())
        self.scene.clear()
        self.boxes = {}
        self.scene.clear_links()

    def update(self):
        super (VisualizerViewer, self).update()
        self.view._scale_fit()

    def sizeHint (self):
        size = QSize()
        size.setWidth(600)
        return size



