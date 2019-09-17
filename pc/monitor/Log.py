from PyQt5.QtWidgets import QTextBrowser, QLineEdit
from Timer import Timer
from StdWrapper import StdWrapper
from StdLogsWrapper import *
from Shell import Shell
import sys
import os

class Log:
    def __init__(self, mainWindow = 0):
        #sys.stderr = StdWrapper(self.error)
        sys.stdout = StdLogsWrapper(self)

        self.savedLogs = ""
        self.correctInit = False

        self.timer = Timer()
        self.timer.start()


        self.log_path = "log.html"

        self.file = open(self.log_path, 'w', newline='')

        if mainWindow == 0: return

        self.init(mainWindow)

    def init(self, mainWindow):
        self.browser = QTextBrowser(mainWindow)
        self.browser.setHtml("<p align='center' style='font-style:italic; font-size: 25px'> DOT. terminal </p>")
        self.console = QLineEdit(mainWindow)

        self.console.returnPressed.connect(self.runCommand)


        self.correctInit = True
        self.addHtml(self.savedLogs)


    def resizeEventP(self, event):
        self.width = self.window.width() - self.edge - 14
        self.height = self.window.height() / 4 - 36

        self.browser.resize(self.width, self.height)
        self.browser.move(self.edge + 7, self.window.height() - 29 - self.height)

        self.console.resize(self.width, 22)
        self.console.move(self.edge + 7, self.window.height() - 29)


    def info(self, str):
        self.addHtml('<span style="color: blue">[{}] INFO:</span> {}'.format(self.timer.getStr(), str))

    def complete(self, str):
        self.addHtml('<span style="color: green">[{}] COMPLETE:</span> {}'.format(self.timer.getStr(), str))

    def warn(self, str):
        self.addHtml('<span style="color: #DAA520">[{}] WARNING:</span> {}'.format(self.timer.getStr(), str))

    def error(self, str):
        self.addHtml('<span style="color: red">[{}] ERROR:</span> {}'.format(self.timer.getStr(), str))

    def output(self, str):
        self.addHtml("<span>{}</span".format(str))

    def addHtml(self, s):
        s = str(s)

        if self.correctInit:
            text = self.browser.toHtml()
            if len(text) < 21000:
                self.browser.setHtml(text + s)
            else:
                self.browser.setHtml(text[text.find("<br/>", len(text)-20000):] + s)
            self.scrollToDown()
            self.file.write(s + "<br/>")
        else:
            self.savedLogs += s + "<br/>"


    def scrollToDown(self):
        bar = self.browser.verticalScrollBar()
        bar.setValue(bar.maximum())

    def runCommand(self):
        Shell().run(self.console.text())
        self.console.setText("")