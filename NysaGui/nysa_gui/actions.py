from PyQt4 import QtCore

_action_instance = None

# Singleton Magic

def Actions(*args, **kw):
    global _action_instance
    if _action_instance is None:
        _action_instance = _Actions(*args, **kw)
    return _action_instance


class _Actions(QtCore.QObject):
    # Nysa GUI Actions
    show_host_view = QtCore.pyqtSignal(name="show_host_view")
    show_ibuilder_view = QtCore.pyqtSignal(name="show_ibuilder_view")
    show_cbuilder_view = QtCore.pyqtSignal(name="show_cbuilder_view")

    host_save = QtCore.pyqtSignal(name="host_save")
    ibuilder_save = QtCore.pyqtSignal(name="ibuilder_save")
    cbuilder_save = QtCore.pyqtSignal(name="cbuilder_save")

    host_open = QtCore.pyqtSignal(name="host_open")
    ibuilder_open = QtCore.pyqtSignal(name="ibuilder_open")
    cbuilder_open = QtCore.pyqtSignal(name="cbuilder_open")
