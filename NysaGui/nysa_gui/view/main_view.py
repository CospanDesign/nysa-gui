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
from functools import partial

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

HOST = "host"
IBUILDER = "ibuilder"
CBUILDER = "cbuilder"

class MainForm(QMainWindow):
    def __init__(self, actions, status, xmsgs, host_view, ibuilder_view, cbuilder_view):
        super (MainForm, self).__init__()
        self.status = status
        self.xmsgs = xmsgs
        self.actions = actions
        self.host_view = host_view
        self.ibuilder_view = ibuilder_view
        self.cbuilder_view = cbuilder_view
        self.setObjectName("main")

        #self.setDockOptions(QMainWindow.ForceTabbedDocks)
        self.host_widget  = QDockWidget("Host View")
        self.host_widget.visibilityChanged.connect(self.host_widget_changed)
        #self.host_widget.setFeatures(   QDockWidget.DockWidgetMovable |
        #                                QDockWidget.DockWidgetFloatable |
        #                                QDockWidget.DockWidgetVerticalTitleBar)
        #self.dock_widget.setAllowedAreas(Qt.TopDockWidgetArea)
        self.host_widget.setWidget(self.host_view)
        self.addDockWidget(Qt.TopDockWidgetArea, self.host_widget)

        self.ibuilder_widget = QDockWidget("IBuilder View")
        self.ibuilder_widget.visibilityChanged.connect(self.ibuilder_widget_changed)
        #self.ibuilder_widget.setFeatures(   QDockWidget.DockWidgetMovable |
        #                                    QDockWidget.DockWidgetFloatable |
        #                                    QDockWidget.DockWidgetVerticalTitleBar)

        self.ibuilder_widget.setWidget(self.ibuilder_view)
        self.addDockWidget(Qt.TopDockWidgetArea, self.ibuilder_widget)

        self.cbuilder_widget = QDockWidget("CBuilder View")
        self.cbuilder_widget.visibilityChanged.connect(self.cbuilder_widget_changed)
        #self.cbuilder_widget.setFeatures(   QDockWidget.DockWidgetMovable |
        #                                    QDockWidget.DockWidgetFloatable |
        #                                    QDockWidget.DockWidgetVerticalTitleBar)

        self.cbuilder_widget.setWidget(self.cbuilder_view)
        self.addDockWidget(Qt.TopDockWidgetArea, self.cbuilder_widget)

        self.status_widget = QDockWidget("Status")
        self.status_widget.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.status_widget.setWidget(self.status)

        self.xmsgs_widget = QDockWidget("Xilinx Builder Messages")
        self.xmsgs_widget.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.xmsgs_widget.setWidget(self.xmsgs)

        self.addDockWidget(Qt.BottomDockWidgetArea, self.status_widget)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.xmsgs_widget)
        self.tabifyDockWidget(self.status_widget, self.xmsgs_widget)
        self.status_widget.raise_()
        self.current_perspective = "host"
        #self.setDocumentMode(True)

        self.setWindowTitle("Nysa")

        ## Actions
        exit_action = QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(quit)

        save_action = QAction("&Save", self)
        save_action.setShortcut('Ctrl+S')

        open_action = QAction("&Open", self)
        open_action.setShortcut('Ctrl+O')

        host_action = QAction('&Host View', self)
        host_action.setShortcut('Ctrl+H')

        ibuilder_action = QAction('&IBuilder View', self)
        ibuilder_action.setShortcut('Ctrl+I')

        cbuilder_action = QAction('&CBuilder View', self)
        cbuilder_action.setShortcut('Ctrl+B')

        save_action.triggered.connect(self.save_clicked)
        open_action.triggered.connect(self.open_clicked)
        host_action.triggered.connect(self.actions.show_host_view)
        ibuilder_action.triggered.connect(self.actions.show_ibuilder_view)
        cbuilder_action.triggered.connect(self.actions.show_cbuilder_view)

        #Show the status window
        status_window_action = QAction("View Status Window", self)
        status_window_action.setShortcut('F4')
        status_window_action.triggered.connect(self.toggle_status_view)

        #Refresh Platform Tree
        #refresh_platform = QAction("Refresh &Platform Tree", self)
        #refresh_platform.setShortcut('F2')
        #refresh_platform.triggered.connect(self.actions.platform_tree_refresh)

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
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)

        nysa_menu = menubar.addMenu('&Nysa')
        #nysa_menu.addAction(refresh_platform)
        nysa_menu.addAction(host_action)
        nysa_menu.addAction(ibuilder_action)
        nysa_menu.addAction(cbuilder_action)

        view_menu = menubar.addMenu('&View')
        view_menu.addAction(status_window_action)

        ma = host_view.get_menu_actions()
        if len(ma) > 0:
            host_menu = menubar.addMenu("&Host")
            for a in ma:
                host_menu.addAction(a)

        ma = ibuilder_view.get_menu_actions()
        if len(ma) > 0:
            ibuilder_menu = menubar.addMenu("&IBuilder")
            for a in ma:
                ibuilder_menu.addAction(a)

        ma = cbuilder_view.get_menu_actions()
        if len(ma) > 0:
            cbuilder_menu = menubar.addMenu("&CBuilder")
            for a in ma:
                cbuilder_menu.addAction(a)


        #self.set_host_view()
        self.tabifyDockWidget(self.host_widget, self.ibuilder_widget)
        self.tabifyDockWidget(self.ibuilder_widget, self.cbuilder_widget)
        self.setTabOrder(self.host_widget, self.ibuilder_widget)
        self.host_widget.raise_()
        #self.host_view.fit()
        self.show()

        self.actions.show_host_view.connect(self.set_host_view)
        self.actions.show_ibuilder_view.connect(self.set_ibuilder_view)
        self.actions.show_cbuilder_view.connect(self.set_cbuilder_view)

    def set_host_view(self):
        self.status.Info("Show Host View")

        #if not self.ibuilder_widget.isFloating():
        #    self.ibuilder_widget.hide()

        #if not self.cbuilder_widget.isFloating():
        #    self.cbuilder_widget.hide()
        self.host_widget.show()
        self.host_widget.raise_()
        self.repaint()

    def set_ibuilder_view(self):
        self.status.Info("Show IBuilder View")
        #if not self.host_widget.isFloating():
        #    self.host_widget.hide()
        #if not self.cbuilder_widget.isFloating():
        #    self.cbuilder_widget.hide()
        self.ibuilder_widget.show()
        self.ibuilder_widget.raise_()
        #app.setFocusWidget(self.ibuilder_widget)
        self.repaint()

    def set_cbuilder_view(self):
        self.status.Info("Show CBuilder View")
        #if not self.host_widget.isFloating():
        #    self.host_widget.hide()
        #if not self.ibuilder_widget.isFloating():
        #    self.ibuilder_widget.hide()
        self.cbuilder_widget.show()
        self.cbuilder_widget.raise_()
        self.repaint()

    def closeEvent(self, event):
        super (MainForm, self).closeEvent(event)
        quit()

    def toggle_status_view(self):
        if self.status_widget.isVisible():
            self.status_widget.setVisible(False)
            self.xmsgs_widget.setVisible(False)
        else:
            self.status_widget.setVisible(True)
            self.xmsgs_widget.setVisible(True)

    def save_clicked(self):
        if self.focused_widget == "host":
            self.status.Debug("Save Host Action!")
            self.actions.host_save.emit()
        elif self.focused_widget == "ibuilder":
            self.status.Debug("Save IBuilder Action!")
            self.actions.ibuilder_save.emit()
        elif self.focused_widget == "cbuilder":
            self.status.Debug("Save CBuilder Action!")
            self.actions.cbuilder_save.emit()
        else:
            #print "Unknown save location"
            pass

    def open_clicked(self):
        if self.focused_widget == "host":
            self.status.Debug("Open Host Action!")
            self.actions.host_open.emit()
        elif self.focused_widget == "ibuilder":
            self.status.Debug("Open IBuilder Action!")
            self.actions.ibuilder_open.emit()
        elif self.focused_widget == "cbuilder":
            self.status.Debug("Open CBuilder Action!")
            self.actions.cbuilder_open.emit()

        else:
            #print "Unknown open location"
            pass

    def host_widget_changed(self, value):
        #print "host widget: %s" % str(value)
        if value:
            self.focused_widget = "host"
        
    def ibuilder_widget_changed(self, value):
        #print "ibuilder widget: %s" % str(value)
        if value:
            self.focused_widget = "ibuilder"

    def cbuilder_widget_changed(self, value):
        #print "cbuilder widget: %s" % str(value)
        if value:
            self.focused_widget = "cbuilder"

