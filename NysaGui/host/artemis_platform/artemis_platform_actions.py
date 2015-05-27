import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

class ArtemisActions(QtCore.QObject):

    #Raw Register signals
    artemis_refresh = QtCore.pyqtSignal(name = "artemis_refresh")

