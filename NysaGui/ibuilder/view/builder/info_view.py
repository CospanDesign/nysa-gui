# -*- coding: utf-8 *-*

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
  07/20/2013: Initial commit
'''

import os
import sys
import json

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from defines import NO_BOARD_IMAGE
from defines import GENERIC_BOARD_IMAGE

from nysa.ibuilder.lib import utils


MANUAL_SELECT_NAME = "Manually Select Project Directory"

NO_PROJECT_SELECTED = "<No Project Selected>"
NO_DIRECTORY_SELECTED = "<No Directory Selected>"
NO_BOARD_SELECTED = "<No Board Selected>"

class InfoView(QWidget):

    def __init__(self, actions, status):
        super(InfoView, self).__init__()
        self.actions = actions
        self.status = status
        self.board_url = ""
        self.board_image = None

        self.project_name_label = QLabel(NO_PROJECT_SELECTED)
        self.directory_label = QLabel(NO_DIRECTORY_SELECTED)
        self.board_name_link = QLabel(NO_BOARD_SELECTED)
        self.status = QLabel(NO_PROJECT_SELECTED)

        self.board_name_link.linkActivated.connect(self.board_link_activated)

        #Add the project/board inforamtion to the grid
        layout = QHBoxLayout()

        info_layout = QFormLayout()
        info_layout.addRow("Project Name", self.project_name_label)
        info_layout.addRow("Directory", self.directory_label)
        info_layout.addRow("Board Name", self.board_name_link)
        info_layout.addRow("Status", self.status)

        #Add the board image
        self.image_view = QLabel("No Image")
        self.board_image_view = QPixmap(NO_BOARD_IMAGE)
        self.image_view.setPixmap(self.board_image_view)

        layout.addLayout(info_layout)
        layout.addWidget(self.image_view)

        self.setLayout(layout)
        #self.actions.update_project_name.connect(self.set_project_name)

    def set_controller(self, controller):
        self.controller = controller
        self.actions.update_view.connect(self.update_view)

    def update_view(self):
        self.set_project_name(None, self.controller.get_project_name())
        self.set_project_directory(self.controller.get_project_location())
        self.set_board_dict(self.controller.get_board_dict())

    def set_project_name(self, prev_project_name, project_name):
        self.project_name_label.setText(project_name)

    def set_project_directory(self, directory):
        self.directory_label.setText(directory)

    def set_board_dict(self, board_dict):
        self.board_dict = board_dict
        name = board_dict["board_name"]
        self.board_name_link.setText(name)
        self.board_directory = utils.get_board_directory(name)
        self.board_url = None
        if "image" not in self.board_dict:
            return
        image_path = os.path.join(self.board_directory, str(name).lower(), "board", self.board_dict["image"])
        print "Image path: %s" % image_path
        self.set_board_image_view(image_path)

    def board_link_activated(self, link):
        #Don't use this link (it sucks), use the link in self.board_url
        if self.board_url is None:
            print "Board URL is None"
            return

        print "Open link at %s" % self.board_url

    def set_board_image_view(self, filename):
        self.board_image_view = QPixmap(filename)
        self.image_view.setPixmap(self.board_image_view)

    def set_status(self, status):
        self.status.setText(status)

    def reset_labels(self):
        self.set_project_name(NO_PROJECT_SELECTED)
        self.set_project_directory(NO_DIRECTORY_SELECTED)
        self.set_board_name(NO_BOARD_SELECTED)
        self.board_image_view = QPixmap(NO_BOARD_IMAGE)
        self.image_view.setPixmap(self.board_image_view)


