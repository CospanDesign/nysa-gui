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


__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from info_view import InfoView
from build_flow_view import BuildFlowView
from build_status import STATUS as BUILD_STATUS

p = os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             "common",
                             "xmsgs_tree_model")
p = os.path.abspath(p)
from xmsgs_tree_model import xmsgs_tree_model
from xmsg_viewer import XmsgViewer


from defines import GEN_ID
from defines import SYNTHESIZER_ID
from defines import TRANSLATOR_ID
from defines import MAP_ID
from defines import PAR_ID
from defines import BITGEN_ID
from defines import TRACE_ID
from defines import DOWNLOADER_ID

class Builder(QWidget):

    def __init__(self, actions, status):
        super (Builder, self).__init__()
        self.status = status
        self.actions = actions
        self.config = {}

        layout = QVBoxLayout()

        self.info = InfoView(actions, status)
        self.bfv = BuildFlowView(actions, status)
        self.xv = XmsgViewer(None, self.actions, self.status)
        self.xv.hide()

        layout.addWidget(self.info)
        layout.addWidget(self.bfv)
        #layout.addWidget(self.tpv)
        layout.addWidget(self.xv)
        self.setLayout(layout)

        self.proc = QProcess()
        self.proc.finished.connect(self.process_finished)
        self.proc.readyReadStandardOutput.connect(self.process_read_standard_output)
        self.proc.readyReadStandardError.connect(self.process_read_standard_error)
        self.proc.error.connect(self.process_error)
        self.proc.started.connect(self.process_started)
        #print "xmsgs tree model: %s" % str(dir(xmsgs_tree_model))
        self.xmodel = xmsgs_tree_model.XmsgsTreeModel()
        self.ibuilder_project_path = None

    def reset(self):
        self.xv.set_model(None)
        self.bfv.reset_status()

    def update(self):
        '''
        self.xv.set_model(self.xmodel)
        self.xmsgs_path = os.path.join(self.gen_dir, "_xmsgs")
        if os.path.exists(self.xmsgs_path):
            self.xmodel.set_path(self.xmsgs_path)
        else:
            self.xmodel.set_path(None)
        self.update_build_status()
        '''
        pass

    def process_finished(self, exit_code, exit_status):
        target = "test"
        data = self.proc.readAllStandardError()
        print "Finish execution: for %s: Exit Code: %d, Exit Status: %d" % (target, exit_code, exit_status)
        print "%s" % str(data)

    def process_read_standard_output(self):
        data = self.proc.readAllStandardOutput()
        print "%s" % str(data),

    def process_read_standard_error(self):
        print "refresh error"
        data = self.proc.readAllStandardError()
        print "%s" % str(data),

    def process_error(self, process_error):
        print "Error While building: %s" % str(process_error)

    def process_started(self):
        print "started"

    def set_controller(self, controller):
        self.info.set_controller(controller)
        self.bfv.set_controller(controller)
        self.controller = controller
        self.bfv.set_build_callback(self.build_callback)

    def set_project_name(self, name):
        self.info.set_project_name(None, name)

    def set_project_directory(self, path):
        self.info.set_project_directory(path)

    def set_board_dict(self, board_dict):
        self.info.set_board_dict(board_dict)

    def build_callback(self, builder_id):

        if builder_id == GEN_ID:
            if not self.generate_project():
                return False
        elif builder_id == SYNTHESIZER_ID:
            if not self.generate_project():
                return False
            self.external_build_tool("xst")

        elif builder_id == TRANSLATOR_ID:
            if not self.generate_project():
                return False
            self.external_build_tool("ngd")

        elif builder_id == MAP_ID:
            if not self.generate_project():
                return False
            self.external_build_tool("map")

        elif builder_id == PAR_ID:
            if not self.generate_project():
                return False
            self.external_build_tool("par")

        elif builder_id == BITGEN_ID:
            if not self.generate_project():
                return False
            self.external_build_tool("bitgen")

        elif builder_id == TRACE_ID:
            if not self.generate_project():
                return False
            self.external_build_tool("trace")

        elif builder_id == DOWNLOADER_ID:
            if not self.generate_project():
                return False
            self.external_build_tool("bitgen")
            self.download_image()

        else:
            self.status.Error("Unrecognize Builder ID: %d" % builder_id)
            return False

        return True

    def download_image(self):
        print "download image"

    def external_build_tool(self, build_command):
        print "external build tool: %s" % build_command
        self.proc.setWorkingDirectory(self.controller.get_generated_project_path())
        env = QProcessEnvironment.systemEnvironment()
        self.proc.setProcessEnvironment(env)
        self.proc.closeWriteChannel()
        self.proc.start("scons", [build_command])

    def generate_project(self):
        result = self.controller.generate_image()
        self.ibuilder_project_path = self.controller.get_generated_project_path()
        if result:
            self.bfv.set_status(GEN_ID, BUILD_STATUS.pass_build)
            self.bfv.set_status(SYNTHESIZER_ID, BUILD_STATUS.ready)
            self.bfv.set_status(TRANSLATOR_ID, BUILD_STATUS.ready)
            self.bfv.set_status(MAP_ID, BUILD_STATUS.ready)
            self.bfv.set_status(PAR_ID, BUILD_STATUS.ready)
            self.bfv.set_status(BITGEN_ID, BUILD_STATUS.ready)
            self.bfv.set_status(TRACE_ID, BUILD_STATUS.ready)
            self.bfv.set_status(DOWNLOADER_ID, BUILD_STATUS.ready)
            return True
        else:
            self.bfv.set_status(GEN_ID, BUILD_STATUS.fail)
            return False

    def set_project_status(self, status):
        self.info.set_status(status)
