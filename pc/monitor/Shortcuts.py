from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence

from Constants import *

class Shortcut(QShortcut):
    def __init__(self, mainWindow, keyCode, command):
        super().__init__(keyCode, mainWindow)

        self.activated.connect(self.active)
        self.shell = mainWindow.shell
        self.command = command

    def active(self):
        if type(self.command) == list:
            for cmd in self.command:
                self.shell.run(cmd)
        else:
            cmd = str(self.command)
            self.shell.run(cmd)


class Shortcuts:
    def __init__(self, mainWindow):
        self.shortcut = {}

        for key in SHORTCUTS:
            for code in [ord(key), ord(key.upper())]:
                self.shortcut[code] = Shortcut(mainWindow, QKeySequence(code), SHORTCUTS[key])
