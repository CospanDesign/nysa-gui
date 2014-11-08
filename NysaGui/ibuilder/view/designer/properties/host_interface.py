import sys
import os
import time

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from properties_base import PropertiesBase

class HostInterfaceProperties(PropertiesBase):

    def __init__(self, status, actions):
        super (HostInterfaceProperties, self).__init__(status, actions)
        self.initialize_default_form_view()

        self.set_name("Host Interface")
        self.set_info("Facilitates communication between host and nysa platfrom")
                        
        self.hide()

    def set_config_dict(self, config_dict):
        self.config_dict = config_dict
        #Setup the reset of the config dict
