# Distributed under the MIT licesnse.
# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#of the Software, and to permit persons to whom the Software is furnished to do
#so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

'''
Log
  6/12/2013: Initial commit
'''

import os
import sys

from PyQt4.QtGui import *
from PyQt4.QtCore import *

image_path = os.path.join(os.path.dirname(__file__),
                          "images")


sys.path.append(os.path.join(os.path.dirname(__file__),
                          os.pardir,
                          os.pardir,
                          os.pardir,
                          "common"))



NO_BOARD_IMAGE = os.path.join(image_path, "noboardselected.png")
GENERIC_BOARD_IMAGE = os.path.join(image_path, "genericboard.png")

GEN_COLOR = QColor("green")
GEN_POS = QPointF(-800, -200)
GEN_RECT = QRectF(0, 0, 200, 100)
GEN_NAME = "Generate Image"
GEN_ID = "gen_image"
GEN_DESC = "Generates code to create an FPGA image"

SYNTHESIZER_COLOR = QColor("blue")
SYNTHESIZER_POS = QPointF(-800, 0)
SYNTHESIZER_RECT = QRectF(0, 0, 200, 100)
from xmsgs.defines import SYNTHESIZER_NAME
from xmsgs.defines import SYNTHESIZER_ID
from xmsgs.defines import SYNTHESIZER_DESC
#SYNTHESIZER_NAME = "Synthesizer"
#SYNTHESIZER_ID = "xst"
#SYNTHESIZER_DESC = "Compile/Combine/Generate binary abstract model"

TRANSLATOR_COLOR = QColor("blue")
TRANSLATOR_POS = QPointF(-400, 0)
TRANSLATOR_RECT = QRectF(0, 0, 200, 100)
from xmsgs.defines import TRANSLATOR_NAME
from xmsgs.defines import TRANSLATOR_ID
from xmsgs.defines import TRANSLATOR_DESC
#TRANSLATOR_NAME = "Translator"
#TRANSLATOR_ID = "ngdbuild"
#TRANSLATOR_DESC = "Translate binary abstract HDL to Xilinx primitives"

MAP_COLOR = QColor("blue")
MAP_POS = QPointF(0, 0)
MAP_RECT = QRectF(0, 0, 200, 100)
from xmsgs.defines import MAP_NAME
from xmsgs.defines import MAP_ID
from xmsgs.defines import MAP_DESC
#MAP_NAME = "Map"
#MAP_ID = "map"
#MAP_DESC = "Map Xilinx prmitives to the FPGA"

PAR_COLOR = QColor("blue")
PAR_POS = QPointF(400, 0)
PAR_RECT = QRectF(0, 0, 200, 100)
from xmsgs.defines import PAR_NAME
from xmsgs.defines import PAR_ID
from xmsgs.defines import PAR_DESC
#PAR_NAME = "PAR"
#PAR_ID = "par"
#PAR_DESC = "Place and route the design within the FPGA"

BITGEN_COLOR = QColor("blue")
BITGEN_POS = QPointF(800, 0)
BITGEN_RECT = QRectF(0, 0, 200, 100)
from xmsgs.defines import BITGEN_NAME
from xmsgs.defines import BITGEN_ID
from xmsgs.defines import BITGEN_DESC
#BITGEN_NAME = "Bitgen"
#BITGEN_ID = "bitgen"
#BITGEN_DESC = "Generate code that can be downloaded to the FPGA"

TRACE_COLOR = QColor("blue")
TRACE_POS = QPointF(800, -200)
TRACE_RECT = QRectF(0, 0, 200, 100)
from xmsgs.defines import TRACE_NAME
from xmsgs.defines import TRACE_ID
from xmsgs.defines import TRACE_DESC
#TRACE_NAME = "Trace"
#TRACE_ID = "trce"
#TRACE_DESC = "Timig analysis"

DOWNLOADER_COLOR = QColor("blue")
DOWNLOADER_POS = QPointF(1200, 0)
DOWNLOADER_RECT = QRectF(0, 0, 200, 100)
DOWNLOADER_NAME = "Downloader"
DOWNLOADER_ID = "downloader"
DOWNLOADER_DESC = "Download image to board"

LINK_COLOR = QColor("black")

BEZIER_CONNECTION = False

BUILD_STATUS_UNKNOWN = os.path.join(image_path, "unknown.png")
BUILD_STATUS_READY = os.path.join(image_path, "ready.png")
BUILD_STATUS_STOP = os.path.join(image_path, "stop.png")
BUILD_STATUS_BUILD = [os.path.join(image_path, "go1.png"),
                      os.path.join(image_path, "go2.png"),
                      os.path.join(image_path, "go3.png"),
                      os.path.join(image_path, "go4.png"),
                      os.path.join(image_path, "go5.png"),
                      os.path.join(image_path, "go6.png")]
BUILD_STATUS_PASS = os.path.join(image_path, "pass.png")
BUILD_STATUS_PASS_WARNINGS = os.path.join(image_path, "passwithwarnings.png")
BUILD_STATUS_FAIL = os.path.join(image_path, "fail.png")
BUILD_STATUS_TIME_STEP = 200

