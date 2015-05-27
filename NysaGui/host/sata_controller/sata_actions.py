import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

class ArtemisUSB2Actions(QtCore.QObject):

    #Raw Register signals
    artemis_refresh = QtCore.pyqtSignal(name = "artemis_refresh")

    pcie_rx_reset        = QtCore.pyqtSignal(bool, name = "pcie_rx_reset")
    pcie_rx_polarity     = QtCore.pyqtSignal(bool, name = "pcie_rx_polarity")
    pcie_reset           = QtCore.pyqtSignal(bool, name = "pcie_reset")
    sata_reset           = QtCore.pyqtSignal(bool, name = "sata_reset")
    gtp_preamp_changed   = QtCore.pyqtSignal(int,  name = "gtp_preamp_changed")
    gtp_tx_swing_changed = QtCore.pyqtSignal(int,  name = "gtp_tx_swing_changed")

