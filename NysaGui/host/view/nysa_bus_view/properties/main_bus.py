import sys
import os
import time

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from properties_base import PropertiesBase

class MainBusProperties(PropertiesBase):

    def __init__(self, status, actions):
        #super (MainBusProperties, self).__init__(parent)
        super (MainBusProperties, self).__init__(status, actions)
        self.initialize_script_list()

        self.layout = QFormLayout(self)
        self.name_label = QLabel("")
        self.name = QLabel("")

        self.info_text = QLabel("")
        self.info_text.setText("Select a module block or select an image script")
        self.info_text.setWordWrap(True)

        self.setLayout(self.layout)
        self.layout.addRow(QLabel("Name"), self.name_label)
        self.layout.addRow(QLabel("Info"), self.info_text)
        self.layout.addRow(QLabel("Scripts"), self.script_list)
        self.hide()


    def set_config_dict(self, name, config_dict, n, scripts):
        self.config_dict = config_dict
        self.nysa = n
        self.clear_scripts_list()
        #print "scripts: %s" % str(scripts)
        self.set_scripts_list(scripts)
        #Setup the reset of the config dict
        self.name_label.setText("%s:%s" % (config_dict["board"], name))
        self.name.setText(name)
        #print "config dict: %s" % str(config_dict)
