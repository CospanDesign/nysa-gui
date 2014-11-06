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

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class MainPanel(QWidget):
    def __init__(self, actions, status, host_view, ibuilder_view, cbuilder_view):
        super(MainPanel, self).__init__()
        layout = QVBoxLayout()
        self.actions = actions
        self.status = status
        self.host_view = host_view
        self.host_view.hide()
        self.ibuilder_view = ibuilder_view
        self.ibuilder_view.hide()
        self.cbuilder_view = cbuilder_view
        self.cbuilder_view.hide()

        self.host_widget  = QDockWidget("Host View")
        #self.dock_widget.setAllowedAreas(Qt.TopDockWidgetArea)
        self.host_widget.setWidget(self.host_view)
        self.addDockWidget(self.host_widget)

        self.ibuilder_widget = QDockWidget("IBuilder View")
        self.ibuilder_widget.setWidget(self.ibuilder_view)

        self.cbuilder_widget = QDockWidget("CBuilder View")
        self.cbuilder_widget.setWidget(self.cbuilder_view)
        
        layout.addWidget(self.host_widget)
        #layout.addWidget(self.host_view)
        #layout.addWidget(self.ibuilder_view)
        #layout.addWidget(self.cbuilder_view)
        layout.addWidget(self.status)

        self.setLayout(layout)

class MainForm(QMainWindow):
    def __init__(self, actions, status, host_view, ibuilder_view, cbuilder_view):
        super (MainForm, self).__init__()
        self.status = status
        self.actions = actions
        self.host_view = host_view
        self.ibuilder_view = ibuilder_view
        self.cbuilder_view = cbuilder_view


        self.host_widget  = QDockWidget("Host View")
        #self.dock_widget.setAllowedAreas(Qt.TopDockWidgetArea)
        self.host_widget.setWidget(self.host_view)
        self.addDockWidget(Qt.TopDockWidgetArea, self.host_widget)

        self.ibuilder_widget = QDockWidget("IBuilder View")
        self.ibuilder_widget.setWidget(self.ibuilder_view)
        self.addDockWidget(Qt.TopDockWidgetArea, self.ibuilder_widget)

        self.cbuilder_widget = QDockWidget("CBuilder View")
        self.cbuilder_widget.setWidget(self.cbuilder_view)
        self.addDockWidget(Qt.TopDockWidgetArea, self.cbuilder_widget)
 
        self.status_widget = QDockWidget("Status")
        self.status_widget.setWidget(self.status)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.status_widget)



        self.setWindowTitle("Nysa")
        #self.host_view = MainPanel(status, actions)
        #self.main_panel = MainPanel(actions, status, host_view, ibuilder_view, cbuilder_view)

        #self.setCentralWidget(self.main_panel)


        #### Actions

        #Exit the application
        exit_action = QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(quit)

        host_action = QAction('&Host View', self)
        host_action.setShortcut('Ctrl+H')

        ibuilder_action = QAction('&IBuilder View', self)
        ibuilder_action.setShortcut('Ctrl+I')

        cbuilder_action = QAction('&CBuilder View', self)
        cbuilder_action.setShortcut('Ctrl+B')

        host_action.triggered.connect(self.actions.show_host_view)
        ibuilder_action.triggered.connect(self.actions.show_ibuilder_view)
        cbuilder_action.triggered.connect(self.actions.show_cbuilder_view)

        #Show the status window
        status_window_action = QAction("View Status Window", self)
        status_window_action.setShortcut('F4')
        status_window_action.triggered.connect(self.toggle_status_view)

        #Refresh Platform Tree
        refresh_platform = QAction("Refresh &Platform Tree", self)
        refresh_platform.setShortcut('F2')
        refresh_platform.triggered.connect(self.actions.refresh_signal)

        #Toolbar
        self.toolbar = self.addToolBar("main")
        self.toolbar.addAction(exit_action)
        self.toolbar.addAction(host_action)
        self.toolbar.addAction(ibuilder_action)
        self.toolbar.addAction(cbuilder_action)

        #Menubar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(exit_action)

        nysa_menu = menubar.addMenu('&Nysa')
        nysa_menu.addAction(refresh_platform)
        nysa_menu.addAction(host_action)
        nysa_menu.addAction(ibuilder_action)
        nysa_menu.addAction(cbuilder_action)

        view_menu = menubar.addMenu('&View')
        view_menu.addAction(status_window_action)

        self.actions.show_host_view.connect(self.set_host_view)
        self.actions.show_ibuilder_view.connect(self.set_ibuilder_view)
        self.actions.show_cbuilder_view.connect(self.set_cbuilder_view)

        self.set_host_view()
        self.show()


    def set_host_view(self):
        self.status.Info("Show Host View") 

        if not self.ibuilder_widget.isFloating():
            self.ibuilder_widget.hide()
            
        if not self.cbuilder_widget.isFloating():
            self.cbuilder_widget.hide()
        self.host_widget.show()
        self.repaint()

    def set_ibuilder_view(self):
        self.status.Info("Show IBuilder View") 
        if not self.host_widget.isFloating():
            self.host_widget.hide()
        if not self.cbuilder_widget.isFloating():
            self.cbuilder_widget.hide()
        self.ibuilder_widget.show()
        self.repaint()

    def set_cbuilder_view(self):
        self.status.Info("Show CBuilder View") 
        if not self.host_widget.isFloating():
            self.host_widget.hide()
        if not self.ibuilder_widget.isFloating():
            self.ibuilder_widget.hide()
        self.cbuilder_widget.show()
        self.repaint()



    def closeEvent(self, event):
        super (MainForm, self).closeEvent(event)
        quit()

    def toggle_status_view(self):
        if self.status.isVisible():
            self.status.setVisible(False)
        else:
            self.status.setVisible(True)


