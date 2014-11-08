



import sys
import os
import time

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *


os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

from graphics_scene import GraphicsScene
from graphics_view import GraphicsView


p = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            os.pardir,
                                            os.pardir,
                                            os.pardir,
                                            os.pardir))


p = os.path.abspath(p)
sys.path.append(p)

from NysaGui.common.pvg.visual_graph.graphics_widget import GraphicsWidget

class FPGABusView(GraphicsWidget):

    def __init__(self, parent, status, actions):
        self.status = status
        self.actions = actions
        #Create a view
        self.view = GraphicsView(parent)
        #Create a scene
        self.scene = GraphicsScene(self.view, status, actions)
        super (FPGABusView, self).__init__(self.view, self.scene)
        self.boxes = {}
        self.show()
        self.fi = parent

    def clear(self):
        #self.status.Verbose( "Clearing the FPGA Image")
        #print "Items: %s" % str(self.view.items())
        self.scene.clear()
        self.boxes = {}
        self.scene.clear_links()

    def update(self):
        super (FPGABusView, self).update()
        self.view._scale_fit()
        #self.scene.update(self.scene.sceneRect())
        #self.scene.invalidate(self.scene.sceneRect())

    def sizeHint (self):
        size = QSize()
        size.setWidth(600)
        return size

