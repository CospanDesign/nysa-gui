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


""" nysa base controller
"""


from PyQt4.Qt import QObject



class ScriptPlugin(type):

    def __init__(cls, name, bases, attrs):
        if cls is None:
            return
        if not hasattr(cls, 'plugins'):
            #print "Initialize plugins"
            '''
            This is only implemented when the metaclass is first instantiated

            Create the class variable
            '''
            cls.plugins = []
        else:
            #print "Adding: %s" % str(cls)
            '''
            This is a plugin class so add it to the plugins class variable
            '''
            cls.plugins.append(cls)


class NysaBaseController:

    __metaclass__ = ScriptPlugin

    @staticmethod
    def get_name():
        return APP_NAME

    @staticmethod
    def get_driver():
        return DRIVER

    def __init__(self):
        self.actions = None
        self.status = None
        super(NysaBaseController, self).__init__()

    def _initialize(self, platform, device_index):
        raise NotImplemented("_initialize Not Implemented")

    def set_nysa_viewer_controls(self, actions, status):
        self.actions = actions
        self.status = status

    def start_tab_view(self, platform, device_index = None, status = None):
        self._initialize()

    def get_view(self):
        raise NotImplemented("get_view Not Implemented")

