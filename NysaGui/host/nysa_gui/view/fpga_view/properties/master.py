import sys
import os
import time

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *


from properties_base import PropertiesBase

class MasterProperties(PropertiesBase):

    def __init__(self, status, actions):
        super (MasterProperties, self).__init__(status, actions)
        self.initialize_default_form_view()

        self.features_text = QLabel("2 Bus Controllers\n\n"
                                    "Single or Burst Reads/Writes\n\n"
                                    "Configuration Address Control\n\n"
                                    "Core Dump")
        self.features_text.setWordWrap(True)

        self.set_name("Master")
        self.set_info("Reads/Writes Data to and from the cores and the host")

        self.layout.addRow(QLabel("Features"), self.features_text)


    def set_config_dict(self, config_dict):
        self.config_dict = config_dict
        #Setup the reset of the config dict
