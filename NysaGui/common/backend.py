import sys
from subprocess import check_call
from subprocess import CalledProcessError
from subprocess import PIPE
import os


class Backend(object):

    def __init__(self):
        super (Backend, self).__init__()

    def is_git_installed(self):
        try:
            check_call(["git", "--version"], stdout = PIPE, stderr = PIPE)
        except CalledProcessError:
            return False
        return True

    def is_pip_installed(self):
        try:
            check_call(["pip", "--version"], stdout = PIPE, stderr = PIPE)
        except CalledProcessError:
            return False
        return True

    def is_nysa_installed(self):
        try:
            import nysa
        except CalledProcessError:
            return False
        return True

    def analyze_system(self):
        # See if nysa is available
        print "Looking for Git...",
        if self.is_git_installed():
            print "Found"
        else:
            print "Not Found"

        print "Looking for Pip...",
        if self.is_pip_installed():
            print "Found"
        else:
            print "Not Found"

        print "Looking for Nysa...",

        if self.is_nysa_installed():
            print "Found"
        else:
            print "Not Found"
            print "Attempt to install"
            self.install_nysa_backend()

    def install_nysa_backend(self):
        if self.is_git_installed() and self.is_pip_installed():
            command = ["pip", "install", "--upgrade", "https://github.com/CospanDesign/nysa.git"]
            #Install Git Repository
            if os.name != "nt":
                command.prepend("sudo")

            v = subprocess.call(command)

    def initialize_nysa(self):
        print "Initialize Nysa"
        

                
