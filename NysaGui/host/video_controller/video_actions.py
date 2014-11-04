import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

_video_action_instance = None

#Singleton Magic
def VideoActions(*args, **kw):
    global _video_action_instance
    if _video_action_instance is None:
        _video_action_instance = _VideoActions(*args, **kw)
    return _video_action_instance

class _VideoActions(QtCore.QObject):

    #control
    color_test = QtCore.pyqtSignal(name = "video_color_test")
 
