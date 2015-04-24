import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

class DMAControllerActions(QtCore.QObject):

    #Raw Register signals
    source_commit_pressed = QtCore.pyqtSignal(int, object, name = "source_commit_pressed")
    sink_commit_pressed = QtCore.pyqtSignal(int, object, name = "sink_commit_pressed")
    instruction_commit_pressed = QtCore.pyqtSignal(int, object, name = "instruction_commit_pressed")

