#! /usr/bin/python

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


""" nysa interface
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'


import sys
import os
import json
import collections
from os import listdir
from os.path import isfile

from PyQt4.Qt import *
from PyQt4.QtCore import *


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from nysa.ibuilder.lib import utils
from nysa.common import site_manager
from NysaGui.common.gui_utils import create_hash
from ibuilder_project import IBuilderProject
from view.ibuilder_view import IBuilderView
from ibuilder_actions import Actions


class IBuilderController(QObject):
    def __init__(self, gui_actions, status, xmsgs):
        super(IBuilderController, self).__init__()
        self.gui_actions = gui_actions
        self.status = status
        self.xmsgs = xmsgs
        self.actions = Actions()
        self.view = IBuilderView(self.gui_actions, self.actions, self.status)
        self.project_tree = self.view.get_project_tree()

        #XXX: Demo Stuff!
        ps = self.scan_for_projects()
        if len(ps) == 0:
            self.new_project()
        for p in ps:
            proj = json.load(open(p, 'r'))
            if "PROJECT_NAME" not in proj:
                continue
            name = proj["PROJECT_NAME"]
            #print "project path: %s" % p
            #print "project name: %s" % name
            
            self.add_project(name, p)

        self.project_tree.select_first_item()
        #XXX: End Demo Stuff!
        self.actions.ibuilder_new_project.connect(self.new_project)
        self.gui_actions.ibuilder_save.connect(self.save)
        self.gui_actions.ibuilder_open.connect(self.open)
        self.actions.update_project_name.connect(self.update_project_name)
        #print "projects: %s" % str(p)

    def update_project_name(self, from_name, to_name):
        print "Update project %s to %s" % (from_name, to_name)
        if from_name == to_name:
            self.status.Info("No change to project name!")
            return

        project = self.project_tree.get_project_by_name(from_name)
        self.view.remove_project(from_name)
        project.set_name(to_name)
        self.view.add_project(project)
        project.update_project()

    def new_project(self):
        self.status.Debug("New Project Clicked!")
        new_project_name_base = "project_%d"
        index = 1
        new_project_name = new_project_name_base % index
        project_names = self.get_project_names()
        print "Project names: %s" % str(project_names)
        conflict = True
        while conflict:
            print "ibuilder_controller: name conflict, get a new name!"
            conflict = False
            if new_project_name in project_names:
                conflict = True
                index += 1
                new_project_name = new_project_name_base % index
                continue
        #Create a populated new project
        self.add_project(new_project_name)

    def scan_for_projects(self):
        path = utils.get_user_ibuilder_project_dir()
        self.status.Info("Searching for ibuilder projects...")
        fs = []
        for f in listdir(path):
            if isfile(os.path.join(path, f)):
                if f.endswith(".json"):
                    fs.append(os.path.join(path, f))
        return fs

    def get_project_names(self):
        return self.project_tree.get_project_names()

    def add_project(self, name, path = None):
        self.status.Debug("Add Project: %s" % name)
        ibp = IBuilderProject(self.actions, self.status, self.xmsgs, name, path)
        self.view.add_project(ibp)

    def get_view(self):
        return self.view

    def save(self):
        #print "ibuilder save"
        try:
            project = self.project_tree.get_selected_project()
        except IndexError as ex:
            #Project not highlighted, find out which project is selected by which one is in focus in ibuilder
            project_name = self.view.get_current_project_name()
            self.status.Info("Selecting Project: %s" % project_name)
            #print "project name: %s" % project_name
            project = self.project_tree.get_project_by_name(project_name)
            self.status.Info("Selecting Project (From Project): %s" % project.get_name())

        print "Name: %s" % project.get_name()
        project.save_project()
        self.project_tree.reset()

    def open(self):
        self.status.Important("Open a project")
        initial_dir = utils.get_user_ibuilder_project_dir()
        #initial_dir = utils.get_nysa_user_base()
        #initial_dir = os.path.join(initial_dir, "user_ibuilder_projects")
        path = initial_dir
        file_path = QFileDialog.getOpenFileName(None,
                                        caption = "Select a project to open",
                                        directory = path,
                                        filter = "*.json")

        #print "file path: %s" % file_path
        if len(file_path) == 0:
            self.status.Info("Open Canceled")
            return
        j = json.load(open(file_path, 'r'))
        name = j["PROJECT_NAME"]
        project_names = self.get_project_names()
        if name in project_names:
            #print "Project already found!"
            m = QMessageBox.warning(None,
            "Replace Project %s" % name,
            "Are sure you want to replace the existing project %s with this one?" % name,
            QMessageBox.Yes | QMessageBox.No,
            defaultButton = QMessageBox.Yes)
            if m == QMessageBox.No:
                print "Cancelled"
                return
            project = self.project_tree.get_project_by_name(name)
            self.view.remove_project(name)

        self.add_project(name, file_path)


