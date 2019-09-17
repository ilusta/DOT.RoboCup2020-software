from PyQt5.QtCore import QElapsedTimer

class Timer(QElapsedTimer):
    def __init__(self):
        super().__init__()

    def get(self):
        return self.nsecsElapsed() / 1e9

    def getStr(self):
        return str(self.get())[:8]
