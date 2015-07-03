import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

class SataActions(QtCore.QObject):

    #Raw Register signals
    sata_refresh                     = QtCore.pyqtSignal(name = "sata_refresh")
    sata_reset                       = QtCore.pyqtSignal(bool, name = "sata_reset")
    sata_command_layer_reset         = QtCore.pyqtSignal(bool, name = "command_layer_reset")
    en_hd_int_changed                = QtCore.pyqtSignal(bool, name = "en_hd_int_changed")
    en_dma_activate_int_changed      = QtCore.pyqtSignal(bool, name = "en_dma_activate_int_changed")
    en_d2h_reg_int_changed           = QtCore.pyqtSignal(bool, name = "en_d2h_reg_int_changed")
    en_pio_setup_int_changed         = QtCore.pyqtSignal(bool, name = "en_pio_setup_int_changed")
    en_d2h_data_int_changed          = QtCore.pyqtSignal(bool, name = "en_d2h_data_int_changed")
    en_dma_setup_int_changed         = QtCore.pyqtSignal(bool, name = "en_dma_setup_int_changed")
    en_set_device_bits_int_changed   = QtCore.pyqtSignal(bool, name = "en_set_device_bits_int_changed")
    send_hard_drive_command          = QtCore.pyqtSignal(int, name = "send_hard_drive_command")
    send_hard_drive_features         = QtCore.pyqtSignal(int, name = "send_hard_drive_features")

