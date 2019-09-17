from Constants import *
from time import sleep

from PyQt5.QtCore import QObject, QThread
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget
from Tools import *

import serial
import threading

class SerialMonitor(QObject):

    signal = QtCore.pyqtSignal(str)

    def __init__(self, *args):
        super().__init__()
        if len(args) == 1:
            self.ser = args[0]
            self.loaded = True
        else:
            self.loaded = False

    def set(self, ser):
        self.ser = ser
        self.loaded = True

    @QtCore.pyqtSlot()
    def startContiniousReading(self):
        while self.loaded:
            if self.ser.in_waiting:
                text = [str(int(b)) for b in self.ser.readline()]
                self.signal.emit(" ".join(text))

            sleep(0.0005)

class Serial(QWidget):
    def __new__(cls): # Singleton
        if not hasattr(cls, 'instance'):
            cls.instance = super(Serial, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        super(Serial, self).__init__()

        self.haveGetter = False
        self.getter = []

        self.works = 0
        self.serials = {}
        self.ports = ["None", "None"]

        self.data = {}
        self.index = 0


        self.currentData = {}


        for i in range(2):
            self.currentData[i] = []
            for j in range(SERIAL_MESSAGE_LEN):
                self.currentData[i].append(0)


        self.clear(False)

    @QtCore.pyqtSlot(str)
    def serialCallback(self, text):
        data = [int(el) for el in text.split(" ")]
        if (len(data) - 3) == SERIAL_MESSAGE_LEN:
            self.currentData[int(data[0] - 48)] = [int(el) for el in data[1:-2]]
            print(text)

            if self.haveGetter:
                for f in self.getter:
                    f(self.currentData)

    def addGetter(self, f):
        if not (f in self.getter):
            self.getter.append(f)
            self.haveGetter = True

    def get(self):
        return self.currentData

    def clear(self, stopThr = True):
        self.clearThreads(stopThr)
        self.monitors = [SerialMonitor(), SerialMonitor()]

    def clearThreads(self, stopThr = True):
        if stopThr:
            for thr in self.threads:
                thr.exit()

        self.threads = [QtCore.QThread(self), QtCore.QThread(self)]

    def genSerial(self, port):
        ser = serial.Serial(port, BAUDRATE, timeout = 0)
        if not ser.is_open:
            l_error("Serial can not be open")
        return ser

    def setPort(self, index, port, conn = True):
        if self.ports[index] == port:
            conn = False

        try:
            self.monitors[index].set(self.genSerial(port))
            self.ports[index] = port

            if conn:
                self.connect()
                l_complete("Set port {} success".format(port))
        except:
            l_warn("Bad port {} - ignoring".format(port))

    def setPorts(self, ports):
        if set(self.ports) == set(ports):
            return

        self.ports = ports

        try:
            for i in range(len(ports)):
                self.setPort(i, self.ports[i], False)
            self.connect()

            l_complete("Set ports {} success".format(ports))
        except:
            l_warn("Bad ports {} - ignoring".format(ports))

    def getPort(self, index):
        return self.ports[index]

    def connect(self):
        self.clear()
        for i in range(2):
            self.monitors[i].signal.connect(self.serialCallback)
            self.monitors[i].moveToThread(self.threads[i])
            self.setPort(i, self.ports[i], False)
            self.threads[i].started.connect(self.monitors[i].startContiniousReading)
            self.threads[i].start()
