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


SYNTHESIZER_NAME = "Synthesizer"
SYNTHESIZER_ID = "xst"
SYNTHESIZER_DESC = "Compile/Combine/Generate binary abstract model"

TRANSLATOR_NAME = "Translator"
TRANSLATOR_ID = "ngdbuild"
TRANSLATOR_DESC = "Translate binary abstract HDL to Xilinx primitives"

MAP_NAME = "Map"
MAP_ID = "map"
MAP_DESC = "Map Xilinx prmitives to the FPGA"

PAR_NAME = "PAR"
PAR_ID = "par"
PAR_DESC = "Place and route the design within the FPGA"

BITGEN_NAME = "Bitgen"
BITGEN_ID = "bitgen"
BITGEN_DESC = "Generate code that can be downloaded to the FPGA"

TRACE_NAME = "Trace"
TRACE_ID = "trce"
TRACE_DESC = "Timig analysis"

