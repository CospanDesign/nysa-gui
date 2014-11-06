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


from PyQt4.Qt import QObject
from PyQt4.Qt import QIcon
from PyQt4.Qt import QPixmap
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QSize

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))
class ProjectTabManagerException(Exception):
    pass

class ProjectTabManager(QObject):

    def __init__(self, tab_view, actions, status):
        super (ProjectTabManager, self).__init__()
        self.status = status
        self.actions = actions
        self.tab_view = tab_view
        self.tabs = []
        self.tab_view.setTabsClosable(True)
        self.tab_view.tabCloseRequested.connect(self.tab_remove_request)

    def set_tab_color (self, widget, color):
        index = self.tab_view.indexOf(widget)
        pm = QPixmap(QSize(16, 16))
        pm.fill(color)
        icon = QIcon(pm)
        self.tab_view.setTabIcon(index, icon)

    def add_tab(self, name, widget, removeable = True):
        if name is None:
            name = widget.get_name()

        if widget is None:
            raise ProjectTabManagerException("Error Widget is None!")

        pm = QPixmap(QSize(16, 16))
        pm.fill()
        icon = QIcon(pm)
        self.tab_view.addTab(widget, icon, name)
        self.tabs.append([name, widget])

    def tab_remove_request(self, index):
        widget = self.tab_view.widget(index)
        #if isinstance(widget, FPGAImage):
        #    self.status.Important( "Cannot remove bus view")
        #    return

        for i in range(len(self.tabs)):
            item = self.tabs[i]
            if widget == item[1]:
                del self.tabs[i]
                self.tab_view.removeTab(index)
                self.actions.remove_tab.emit(widget)
                return
        return
