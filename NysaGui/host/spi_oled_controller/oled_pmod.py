# Copyright (c) 2014 Dave McCoy (dave.mccoy@cospandesign.com)

# This file is part of Nysa (wiki.cospandesign.com/index.php?title=Nysa).
#
# Nysa is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# Nysa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Nysa; If not, see <http://www.gnu.org/licenses/>.

import os
import sys

import time
from array import array as Array

from nysa.host.nysa import Nysa
from nysa.host.driver.spi import SPI
from nysa.host.driver.gpio import GPIO


"""
SPI OLED Controller
"""

GPIO_DEVICE_NAME = "GPIO"
GPIO_UNIQUE_ID = 1
SPI_DEVICE_NAME = "SPI"
SPI_UNIQUE_ID = 2

#GPIOs
DATA_COMMAND_MODE = 2
RESET             = 3
VBAT_ENABLE       = 4
VDD_ENABLE        = 5

#SS bit
SLAVE_SELECT_BIT  = 0

#COMMANDS
CONTRAST          = Array('B', [0x81, 0x00])
EN_CHARGE_PUMP    = Array('B', [0x8D, 0x14])
DIS_CHARGE_PUMP   = Array('B', [0x8D, 0x10])

PRE_CHARGE_PER    = Array('B', [0xD9, 0x00])

COMM_SEQ          = Array('B', [0xDA, 0x20])

RESUME_FROM_RAM   = Array('B', [0xA4])
RESUME_DISPLAY    = Array('B', [0xA5])
NON_INVERT_DISPLAY= Array('B', [0xA6])
INVERT_DISPLAY    = Array('B', [0xA7])
DISPLAY_OFF       = Array('B', [0xAE])
DISPLAY_ON        = Array('B', [0xAF])
SET_LOW_ADDRESS   = Array('B', [0x00])
SET_HIGH_ADDRESS  = Array('B', [0x10])
SET_START_LINE    = Array('B', [0x40])


#Device Constants
DISPLAY_SIZE      = 512
PAGE_MAX          = 4
COL_MAX           = 128
ROW_MAX           = 32

FONT_LENGTH       = 8
USER_MAX          = 0x20
FONT_USER_MAX     = USER_MAX * FONT_LENGTH


#drawing mode
DRAW_SET          = 0
DRAW_OR           = 1
DRAW_AND          = 2
DRAW_XOR          = 3



class OLED(object):

    #OLED Functions
    def __init__(self, platform, nui, status):
        gpio_id = platform.find_device(Nysa.get_id_from_name(GPIO_DEVICE_NAME),
                                sub_id = None,
                                unique_id = GPIO_UNIQUE_ID)
        self.status = status
        self.status.Debug("GPIO ID: %s" % str(gpio_id))
        self.gpio = GPIO(platform, gpio_id)
        #Get a reference to SPI
        spi_id = platform.find_device(Nysa.get_id_from_name(SPI_DEVICE_NAME),
                                sub_id = None,
                                unique_id = SPI_UNIQUE_ID)
        self.status.Debug("SPI ID: %s" % str(spi_id))
        self.spi = SPI(platform, spi_id)

        #Setup the controller
        self.platform = platform
        self.status = status
        self.spi.set_spi_clock_rate(1000000)
        self.status.Important("Clock Rate: %d" % self.spi.get_spi_clock_rate())
        #self.spi.set_tx_polarity(False)
        #self.spi.set_rx_polarity(True)
        self.spi.set_spi_mode(3)
        self.spi.set_spi_slave_select(0, True)
        self.spi.auto_ss_control_enable(True)
        self.spi.set_character_length(8)
        self.buffer_len = self.spi.get_max_character_length() / 8

        self.gpio.set_port_direction(0xFFFFFFFF)
        #Setup the GPIOs
        self.set_command_mode()
        self.enable_vdd(False)
        self.enable_vbat(False)
        time.sleep(0.001)

        self.setup()

    def reset(self):
        self.status.Important("Resetting OLED")
        self.gpio.set_bit_value(RESET, 0)
        time.sleep(0.01)
        self.gpio.set_bit_value(RESET, 1)

    def set_data_mode(self):
        self.gpio.set_bit_value(DATA_COMMAND_MODE, 1)

    def set_command_mode(self):
        self.gpio.set_bit_value(DATA_COMMAND_MODE, 0)

    def enable_vbat(self, enable):
        if enable:
            self.gpio.set_bit_value(VBAT_ENABLE, 0)
        else:
            self.gpio.set_bit_value(VBAT_ENABLE, 1)

    def enable_vdd(self, enable):
        if enable:
            self.gpio.set_bit_value(VDD_ENABLE, 0)
        else:
            self.gpio.set_bit_value(VDD_ENABLE, 1)

    def send_command(self, command):
        #if isinstance(command, list):
        #    command = Array('B', command)
        #elif isinstance(command, int):
        #    command = Array('B', [command])
        command = Array('B', [command])
        #print "command: %s" % str(command)
        self.spi.set_write_data(command)
        self.spi.start_transaction()
        #XXX: This should be pushed to a background thread!
        while self.spi.is_busy():
            time.sleep(0.01)

    def write_buffer(self, buf):
        column_index = 0
        for i in range(4):
            #Set the Page command
            self.set_command_mode()
            self.send_command(0x22)
            self.send_command(i)

            #Start from the left column
            self.send_command(0x00)
            self.send_command(0x10)

            self.set_data_mode()
            self.put_column_buffer(i, buf)

    def put_column_buffer(self, column_index, buf):
        pos = 0
        column_width = 128

        buf_pos = column_index * column_width
        last_buf_pos = buf_pos + column_width

        #self.buffer_len
        for i in range ((column_index * 128), ((column_index * 128) + 128)):
            #self.send_command(Array('B', [buf[i]]))
            self.spi.set_write_data([buf[i]])
            self.spi.start_transaction()
            while self.spi.is_busy():
                time.sleep(0.01)

    def setup(self):
        self.status.Important("Power Up")

        self.set_command_mode()

        self.status.Important("Enable VDD")
        self.enable_vdd(True)
        time.sleep(0.001)


        #Disable the Display
        self.status.Important("Disable display")
        self.send_command(0xAE)

        #Reset the display
        self.status.Important("Reset display")
        self.reset()

        #Set the charge pump and set pre-charge period command
        self.status.Important("Setup charge pump and pre-charge pump")
        self.send_command(0x8D)
        self.send_command(0x14)

        self.send_command(0xD9)
        self.send_command(0xF1)

        #Turn on VBAT
        self.status.Important("Turn on VBAT")
        self.enable_vbat(True)
        time.sleep(0.1)

        #Invert the display
        self.status.Important("Invert Display")
        self.send_command(0xA1)    #Remap Columns
        self.send_command(0xC8)    #Remap Rows

        self.status.Important("Set the command to select sequence COMM configuration")
        self.send_command(0xDA)
        self.send_command(0x20)

        self.status.Important("Enable display")
        self.send_command(0xAF)


