from PyQt5.QtGui import QPainter
from Point import Point

class Painter(QPainter):
    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform, True)

    def drawCircle(self, *args):
        if type(args[0]) is Point:
            r = args[1]
            self.drawEllipse(args[0].x - r / 2, args[0].y - r / 2, r, r)
        else:
            r = args[2]
            self.drawEllipse(args[0] - r / 2, args[1] - r / 2, r, r)
