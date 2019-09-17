from PyQt5.QtWidgets import QMenuBar, QMenu, QAction
from PyQt5.QtCore import QTimer

from ColorConstants import *
from Constants import *
from Params import Params
from SerialConfig import *

class MenuWrapper(QMenu):
    # Count - count of active elements in normal work
    # Command - list of commands for actions
    # Text - list of text for actions
    # MinEmptyCount - set minimal count of "checked" icons in menu
    def __init__(self, mainMenu, mainWindow, **kwargs):
        super().__init__(mainMenu)

        if not (("text" in kwargs) and ("command" in kwargs) and ("title" in kwargs) and len(kwargs["command"]) == len(kwargs["text"])):
            raise TypeError("Bad parameters")

        self.text = kwargs["text"]
        self.command = kwargs["command"]
        self.title = kwargs["title"]
        self.setTitle(self.title)

        self.count = kwargs["count"] if ("count" in kwargs) else 1

        self.active = [None for i in range(self.count)]
        self.sz = len(self.text)
        self.actions = [ActionWrapper(mainWindow, text=self.text[i], command=self.command[i],
        eventActivate=self.setActive, eventDeactivate=self.delActive, index=i) for i in range(self.sz)]

        for action in self.actions:
            self.addAction(action)

        if "active" in kwargs:
            active = kwargs["active"]
            if type(active) == int:
                self.setActive(active)
            else:
                for i in active:
                    self.setActive(i)

        self.empty = kwargs["minEmptyCount"] if ("minEmptyCount" in kwargs) else 1

    def setActive(self, index):
        self.active.insert(0, index)
        self.active = self.active[:self.count]
        self.update()

    def delActive(self, index):
        added = -1
        if len(self.active) <= self.empty:
            for i in range(self.sz):
                if not i in self.active:
                    added = i
                    break
        self.active.remove(index)
        if added != -1:
            self.setActive(added)
        self.update()

    def update(self):
        for i in range(self.sz):
            if i in self.active:
                self.actions[i].activate()
            else:
                self.actions[i].deactivate()
            self.actions[i].updateIcon()

class ActionWrapper(QAction):
    def __init__(self, mainWindow, **kwargs):
        super().__init__(mainWindow)

        self.triggered.connect(self.clicked)

        self.icon = TRIGGER_ICON
        self.emptyIcon = NO_ICON

        self.trigger = False

        if "text" in kwargs:
            self.setText(kwargs["text"])

        if "command" in kwargs:
            self.cmd = kwargs["command"]
            self.executableCommand = False
        elif "executableCommand" in kwargs:
            self.executableCommand = True
            self.cmd = kwargs["executableCommand"]

        self.inMenu = False
        if ("eventActivate" in kwargs) and ("eventDeactivate" in kwargs) and ("index" in kwargs):
            self.eventActivate = kwargs["eventActivate"]
            self.eventDeactivate = kwargs["eventDeactivate"]
            self.index = kwargs["index"]
            self.inMenu = True

        if "active" in kwargs: self.active = kwargs["active"]
        else: self.active = False

        self.updateIcon()

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def change(self):
        self.active = not self.active


    def setCommand(self, cmd):
        self.cmd = cmd

    def updateIcon(self):
        if self.active:
            self.setIcon(self.icon)
        else:
            self.setIcon(self.emptyIcon)

    def clicked(self):
        if self.inMenu:
            if self.active:
                self.eventDeactivate(self.index)
            else:
                self.eventActivate(self.index)
        else:
            self.active = not self.active
            self.updateIcon()

        if self.executableCommand:
            self.cmd()

class ComMenuWrapper(QMenu):

    def __init__(self, mainMenu, mainWindow, **kwargs):
        super().__init__(mainMenu)
        if not ("title" in kwargs):
            raise TypeError("Bad parameters")

        self.title = kwargs["title"]
        self.setTitle(self.title)

        self.count = kwargs["count"] if ("count" in kwargs) else 1

        self.active = [None for i in range(self.count)]

        self.empty = kwargs["minEmptyCount"] if ("minEmptyCount" in kwargs) else 1

        self.aboutToShow.connect(self.startTimer)
        self.aboutToHide.connect(self.stopTimer)

        self.timer = QTimer()
        self.timer.timeout.connect(self.timerEvent)

        self.timerDelay = 300

        self.oldSerialList = []


    def setActive(self, index):
        self.active.insert(0, index)
        self.active = self.active[:self.count]
        self.update()

    def delActive(self, index):
        added = -1
        if len(self.active) <= self.empty:
            for i in range(self.sz):
                if not i in self.active:
                    added = i
                    break
        self.active.remove(index)
        if added != -1:
            self.setActive(added)
        self.update()

    def update(self):
        for i in range(self.sz):
            if i in self.active:
                self.actions[i].activate()
            else:
                self.actions[i].deactivate()
            self.actions[i].updateIcon()

    def startTimer(self):
        self.updateSerial()
        self.timer.start(self.timerDelay)

    def timerEvent(self):
        self.updateSerial()

    def stopTimer(self):
        self.timer.stop()

    def updateSerial(self):
        serialList = getSerialDevices()
        if self.oldSerialList != serialList:
            self.sz = len(serialList)
            self.clear()

            self.actions = [ActionWrapper(self, text=extractName(serialList[i]), executableCommand=self.updateBots,
            eventActivate=self.setActive, eventDeactivate=self.delActive, index=i) for i in range(self.sz)]

            for action in self.actions: self.addAction(action)
            self.oldSerialList = serialList



class MenuBar(QMenuBar):

    def __init__(self, mainWindow):
        super().__init__(mainWindow)

        self.params = Params()

        self.move(0,0)
        self.setObjectName("menubar")
        self.settings = QMenu(self)
        self.colorMenu = MenuWrapper(self.settings, mainWindow, title="Set colormode", text=["Lightmode", "Nightmode"], command=["lightmode", "nightmode"])
        self.comMenu = ComMenuWrapper(self.settings, mainWindow, title="Set COM-port", count=2, minEmptyCount=0)
        self.modeMenu = MenuWrapper(self.settings, mainWindow, title="Set mode", text=["Normal", "Simulator"], command=["set mode normal", "set mode simulator"])
        self.colorMenu.setActive(0)
        self.modeMenu.setActive(0)

        self.exit = ActionWrapper(mainWindow, text="Exit", command="exit")

        self.settings.addAction(self.modeMenu.menuAction())
        self.settings.addAction(self.comMenu.menuAction())
        self.settings.addAction(self.colorMenu.menuAction())
        self.settings.addSeparator()
        self.settings.addAction(self.exit)
        self.addAction(self.settings.menuAction())

        self.settings.setTitle("Settings")

    def resizeEventP(self, event):
        self.resize(self.window.width(), 22)