# This is only needed for Python v2 but is harmless for Python v3.

from PyQt4 import QtCore
from PyQt4 import QtGui

import sip
sip.setapi('QVariant', 2)

try:
    from PyQt4.phonon import Phonon
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "Phonon Capabilities",
            "Your Qt installation does not have Phonon support.",
            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
            QtGui.QMessageBox.NoButton)
    sys.exit(1)




