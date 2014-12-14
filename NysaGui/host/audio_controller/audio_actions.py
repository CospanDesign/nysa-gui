import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.Qt import *

_audio_action_instance = None

#Singleton Magic
def AudioActions(*args, **kw):
    global _audio_action_instance
    if _audio_action_instance is None:
        _audio_action_instance = _AudioActions(*args, **kw)
    return _audio_action_instance

class _AudioActions(QObject):
    play_audio = pyqtSignal(name = "play_audio")
    pause_audio = pyqtSignal(name = "pause_audio")
    stop_audio = pyqtSignal(name = "stop_audio")
    play_1khz = pyqtSignal(name = "1khz_audio")
    set_audio_file = pyqtSignal(object, name = "set_audio_file")
    set_audio_position = pyqtSignal(float, name = "set_audio_position")

    convert_audio_update = pyqtSignal(int, name = "convert_audio_update")
    update_total_chunk_count = pyqtSignal(int, name = "update_total_chunk_count")
