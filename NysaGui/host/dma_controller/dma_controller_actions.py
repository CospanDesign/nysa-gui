import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

class DMAControllerActions(QtCore.QObject):

    #Raw Register signals
    source_commit = QtCore.pyqtSignal(int, object, name = "source_commit_pressed")
    sink_commit = QtCore.pyqtSignal(int, object, name = "sink_commit_pressed")
    instruction_commit = QtCore.pyqtSignal(int, object, name = "instruction_commit_pressed")

    enable_dma = QtCore.pyqtSignal(bool, name = "enable_dma")
    channel_enable = QtCore.pyqtSignal(int, bool, name = "enable_channel")

