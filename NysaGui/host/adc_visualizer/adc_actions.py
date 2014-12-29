import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

_adc_action_instance = None

#Singleton Magic
def ADCActions(*args, **kw):
    global _adc_action_instance
    if _adc_action_instance is None:
        _adc_action_instance = _ADCActions(*args, **kw)
    return _adc_action_instance

class _ADCActions(QtCore.QObject):

    #Token Add/Remove 
    adc_token_add = QtCore.pyqtSignal(int, float, name = "new_reading")

