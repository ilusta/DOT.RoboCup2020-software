from PyQt5.QtWidgets import QTextBrowser
from PyQt5.QtGui import QColor

from Tools import *

class Data:
    def __init__(self, mainWindow, index):
        self.browser = QTextBrowser(mainWindow)

        self.data = {}
        self.data["Battery"] = [12.5, "V"]
        self.data["Line direction"] = [180, "deg"]
        self.data["Ball distance"] = [30, "cm"]
        self.data["Ball direction"] = [85, "deg"]
        self.data["Speed"] = [30, "%"]
        self.data["Angle"] = [12.37, "deg"]
        self.data["Heading"] = [-123.5, "deg"]
        self.data["Have ball"] = ["", ""]
        self.data["Is playing"] = ["", ""]
        self.data["Color"] = ["", ""]

        self.index = index

    def resizeEventP(self, event):
        left_pos = 7 + self.edge + self.index * (self.window.width() - self.edge - 7) / 2

        self.height = 7 * self.window.height() / 12 - 36
        self.width = (self.window.width() - self.edge - 21) / 2

        self.browser.move(left_pos, 29)
        self.browser.resize(self.width, self.height)
        self.userData = []

        self.update()

    def serialUpdate(self, data, userData = []):
        try:
            self.userData = userData
            i = 0
            for key in self.data:
                dt = data[i]
                
                if not type(dt) is bool and not type(dt) is str:
                    if dt < 10: dt = round(dt * 100) / 100
                    elif dt < 100: dt = round(dt * 10) / 10
                    else: dt = int(round(dt))
                
                self.data[key][0] = str(dt)
                i += 1
        except:
            pass

    def update(self):
        bar_value = self.browser.verticalScrollBar().value()
        html = "<p style='font-weight: bold; font-size: 28px;' align='center'>BOT #{}</p><hr/>".format(self.index + 1)
        for key in self.data:
            html += "<span style='font-size: 18px'><b>{}:</b> {}{}</span><br>".format(key, self.data[key][0], self.data[key][1])
        
        html += "<hr/>"
        for val in self.userData:
            html += "<span style='font-size: 16px; color: \"#337\";'><b>{}</b></span><br/>".format(str(int(val)))
        self.browser.setHtml(html)
        self.browser.verticalScrollBar().setValue(bar_value)