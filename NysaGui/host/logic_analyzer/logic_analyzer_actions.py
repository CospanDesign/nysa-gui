import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

class LogicAnalyzerActions(QtCore.QObject):

    #GPIO Specific signals
    trigger_en_changed = QtCore.pyqtSignal(name = "trigger_en_changed")
    trigger_pol_changed = QtCore.pyqtSignal(name = "trigger_pol_changed")
    enable_capture = QtCore.pyqtSignal(bool, name = "enable_capture")
    reset_logic_analyzer = QtCore.pyqtSignal(name = "reset_logic_analyzer")
    repeat_count_changed = QtCore.pyqtSignal(name = "repeat_count_changed")
    trigger_offset_changed = QtCore.pyqtSignal(name = "trigger_offset_changed")
    restart_logic_analyzer = QtCore.pyqtSignal(name = "restart_logic_analyzer")
    repeat_count_update = QtCore.pyqtSignal(name = "repeat_count_update")
    trigger_offset_update = QtCore.pyqtSignal(name = "trigger_offset_update")
    capture_detected = QtCore.pyqtSignal(name = "capture_detected")


