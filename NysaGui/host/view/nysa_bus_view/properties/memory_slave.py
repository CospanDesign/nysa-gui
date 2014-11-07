import sys
import os
import time

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from properties_base import PropertiesBase

class MemorySlaveProperties(PropertiesBase):

    def __init__(self, status, actions):
        super (MemorySlaveProperties, self).__init__(status, actions)

        self.layout = QFormLayout(self)
        self.name = QLabel("")

        self.initialize_script_list()

        self.setLayout(self.layout)
        self.layout.addRow(QLabel("Module Type"), QLabel("Memory Slave"))
        self.layout.addRow(QLabel("Name"), self.name)
        self.layout.addRow(QLabel("Scripts"), self.script_list)
        self.hide()


    def set_slave(self, name, config_dict, n, scripts):
        self.name.setText(name)
        self.clear_scripts_list()
        self.set_scripts_list(scripts)
        self.config_dict = config_dict
        self.nysa = n
        self.name.setText(name)
        #Setup the reset of the config dict
