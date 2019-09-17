from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QFont

SS = 0

class ButtonsSet:
    def __init__(self, mainWindow, index, names, commands, log):
        self.buttons = [PushButton(mainWindow, names[i], commands[i], log) for i in range(len(names))]
        self.buttons.insert(0, SSButton(mainWindow, index))
        self.index = index

    def resizeEventP(self, event):
        left_pos = 7 + self.edge + self.index * (self.window.width() - self.edge - 7) / 2
        self.width = (self.window.width() - self.edge - 21) / 2
        self.height = (self.window.height() / 6 - 14) / len(self.buttons)

        for i in range(len(self.buttons)):
            self.buttons[i].move(left_pos, 7 * self.window.height() / 12 + (self.height + 7) * i)
            self.buttons[i].resize(self.width, self.height)

    def changeText(self, buttonIndex, text):
        pass

class PushButton(QPushButton):
    def __init__(self, mainWindow, name, command, log):
        super().__init__(mainWindow)

        self.setText(name)

        font = self.font()
        font.setPointSize(20)
        font.setWeight(QFont.Bold)
        self.setFont(font)

        self.shell = mainWindow.shell
        self.clicked.connect(self.run)

        self.command = command

    def run(self):
        self.shell.run(self.command)

class SSButton(QPushButton):
    def __init__(self, mainWindow, index):
        super().__init__(mainWindow)

        font = self.font()
        font.setPointSize(20)
        font.setWeight(QFont.Bold)
        self.setFont(font)

        self.shell = mainWindow.shell
        self.clicked.connect(self.run)
        
        self.cmd = "!s " + str(index)
        self.text = ["Start", "Stop"]
        
        self.colors = ["#f99", "#33aa44"]
        
        self.updater(0)
    
    def updater(self, index):
        self.index = index
        self.setStyleSheet("QPushButton {background-color: " + self.colors[self.index] + ";}")
        self.setText(self.text[self.index])
        
    def run(self):
        self.shell.run(self.cmd)
    