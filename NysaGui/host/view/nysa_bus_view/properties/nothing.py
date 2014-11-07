import sys
import os
import time

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *


os.path.join(os.path.dirname(__file__),
             os.pardir,
             os.pardir,
             os.pardir)

from properties_base import PropertiesBase

class NothingProperties(PropertiesBase):

    def __init__(self, status, actions):
        #super (NothingProperties, self).__init__(parent)
        super (NothingProperties, self).__init__(status, actions)

        self.layout = QFormLayout(self)

        self.ilabel = QLabel("Info")
        self.info_text = QLabel("Nothing Selected, Choose a device in the Platform Tree")
        self.info_text.setWordWrap(True)

        self.setLayout(self.layout)
        self.layout.addRow(self.ilabel, self.info_text)
        self.hide()

