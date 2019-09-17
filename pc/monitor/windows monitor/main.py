import sys
import inspect
import math

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5.QtGui import QColor, QPen, QBrush, QImage, QIcon, QPainter
from PyQt5.QtCore import Qt, QTimer

from Constants import *
from ColorConstants import *
from Tools import *

from Data import Data
from ButtonsSet import ButtonsSet
from Log import Log
from Menu import MenuBar
from Painter import Painter
from Point import Point
from Timer import Timer
from Params import Params
from Shell import Shell
from Shortcuts import Shortcuts
import serial
import numpy as np

log = Log()
params = Params()

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'DOT. monitor'
        self.initUI()
        self.showMaximized()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(50, 50, 800, 400)

        # Set window background color
        #self.setAutoFillBackground(True)
        #p = self.palette()
        #p.setColor(self.backgroundRole(), QColor(45, 45, 45))
        #self.setPalette(p)

        self.shell = Shell(self.writer)

        log.init(self)

        self.field = Field(self)
        self.data = [Data(self, 0), Data(self, 1)]
        self.shortcuts = Shortcuts(self)
        
        self.coms = [params.get("com0"), params.get("com1")]
        
        self.serials = []
        for com in self.coms:
            try:
                self.serials.append(serial.Serial("COM" + str(int(com)), 115200, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, timeout = 0))
                l_complete("Succesful connect to {}".format("COM" + str(int(com))))
            except:
                pass

        names = ["Calibrate"]
        commands = ["!c"]
        
        self.playingFuncs = [[], []]
        
        self.buttons = []
        for index in [0, 1]:
            self.buttons.append(ButtonsSet(self, index, names, [(cmd + " " + str(index + 1)) for cmd in commands], log))
            
            try:
                self.addPlayingFunc(index, self.buttons[-1].buttons[0].updater)
            except:
                print("bad")
                pass

        self.menubar = MenuBar(self)

        self.show()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateSerial)
        self.timer.start(8)
        
        
        self.timer2 = QTimer(self)
        self.timer2.timeout.connect(self.field.update)
        self.timer2.start(100)
        
        l_log("Initialization finished")
    
    def writer(self, msg, index = 0):
        try:
            self.serials[index].write(str.encode(msg))
            print("Command is sending..")
        except:
            print("Serial error on write")
    def addPlayingFunc(self, index, f):
        self.playingFuncs[index].append(f)
    
    def updateSerial(self):
        for ser in self.serials:
            if ser.in_waiting:
                l = ser.readline()
                if len(l) >= SERIAL_MESSAGE_LEN and (l[0] == 0 or l[0] == 1):
                    text = np.array([int(b) for b in l], dtype = np.float64)
                    
                    bot = int(text[0])
                    line = (text[1] / 255.0) * 360 - 180
                    ball_dist = text[2]
                    ball_angle = (text[3] / 255.0) * 360 - 180
                    speed = (text[4] / 400.0) * 100
                    bot_angle = (text[5] / 255.0) * 360 - 180
                    heading = (text[6] / 255.0) * 360 - 180
                    enemy_angles = (text[7:9] / 255.0) * 360 - 180
                    enemy_dists = text[9:11]
                    power = text[11] / 10
                    userValues = text[14:-1]
                    
                    info = int(text[12])
                    
                    isPlaying = (info % 2 >= 1)
                    haveBall = ((info % 4) >= 2)
                    ourGoal = ((info % 8) >= 4)
                    
                    self.field.colormode = ourGoal
                    
                    self.data[bot].serialUpdate([power, line, ball_dist, ball_angle, speed, bot_angle, heading, haveBall, isPlaying, "Yellow" if ourGoal else "Blue"], userValues)
                    self.data[bot].update()
                    
                    bot_indexes = [bot]
                    
                    if len(self.serials) == 1:
                        bot_indexes.append(1 - bot)
                        
                    for i in bot_indexes:
                        self.field.robots[i].angle = bot_angle
                        self.field.robots[i].heading = heading
                        self.field.updateRobot(i, 50, 0)
                        self.field.updateBall(i, ball_angle, ball_dist)
                        self.field.updateEnemy(i, enemy_angles, enemy_dists)
                            
                    
                    for f in self.playingFuncs[bot]: f(isPlaying)
                    
                    self.field.resizeEventP()
                    
    
    def resizeEvent(self, event):
        # Save current window size
        self.box = self.geometry()

        self.field.window = self.box
        self.field.resizeEventP(event)

        # Save central edge Point
        edge = self.field.height + 7

        self.menubar.window = self.box
        self.menubar.edge = edge
        self.menubar.resizeEventP(event)
        log.window = self.box
        log.edge = edge
        log.resizeEventP(event)
        for data in self.data:
            data.window = self.box
            data.edge = edge
            data.resizeEventP(event)
            data.update()

        for button in self.buttons:
            button.window = self.box
            button.edge = edge
            button.resizeEventP(event)

class GameObject:

    def __init__(self):
        
        self.c_pos = Point()
        self.d_pos = Point()
        
        self.pos = Point()
        self.r = 1

        self.d_r = 0

        self.speed = 0
        self.move_direction = 0

        self.last = Point()

        self.center = Point()
        self.cm2pix = 1

    def updateSize(self, field):
        self.center = field.center
        self.cm2pix = field.cm2pix

        self.c_pos = self.pos * self.cm2pix
        self.d_pos = self.center + self.c_pos
        
        self.d_r = self.r * self.cm2pix

    def move(self, *args):
        self.last = self.pos.copy()
        if len(args) == 2:
            self.pos.set(args[0], args[1])
        elif len(args) == 1:
            self.pos = args[0]
        else:
            raise TypeError("Bad params")

        self.c_pos = self.pos * self.cm2pix
        self.d_pos = self.center + self.c_pos

class GameUniformObject(GameObject):
    def __init__(self):
        super().__init__()
        
        self.c_pos = Point()
        self.d_pos = Point()
        
        self.current = [Point(20, -10), Point(0, 20)]
        self.d_current = self.current.copy()

    def approximateCurrent(self):
        self.pos = (self.current[0] + self.current[1]) / 2

    def updateSize(self, field):
        super().updateSize(field)

        for i in range(BOT_COUNT): self.d_current[i] = self.center + self.current[i] * self.cm2pix

        self.approximateCurrent()
        self.c_pos = self.pos * self.cm2pix
        self.d_pos = self.center + self.c_pos

        self.linePen.setWidthF(self.cm2pix)

    def move(self, *args):
        self.last = self.pos.copy()
        if len(args) == 4:
            for i in range(BOT_COUNT):
                self.current[i].set(args[i * 2], args[1 + i * 2])
        elif len(args == 2):
            for i in range(BOT_COUNT):
                self.current[i] = args[i]
        else:
            raise TypeError("Bad params")

        self.approximateCurrent()
        self.c_pos = self.pos * self.cm2pix
        self.d_pos = self.center + self.c_pos
    
    def moveByIndex(self, *args):
        self.last = self.pos.copy()
        index = args[0]
        if len(args) == 3:
            self.current[index].set(args[1], args[2])
        elif len(args) == 2:
                self.current[index] = args[1]
        else:
            raise TypeError("Bad params")

        self.approximateCurrent()
        self.c_pos = self.pos * self.cm2pix
        self.d_pos = self.center + self.c_pos
        
    
class Robot(GameObject):

    def __init__(self, index):
        super().__init__()
        
        self.index = index
        
        self.r = ROBOT_RADIUS
        self.smooth = params.get("smooth")
        self.angle = 0
        self.heading = -32

        self.image = QImage("images/bot.png")
        self.d_image = self.image.copy()
        self.image.setDevicePixelRatio(self.smooth)

        self.linePen = QPen(TRUE_RED)
        self.linePen.setCapStyle(Qt.RoundCap)

    def updateSize(self, field):
        super().updateSize(field)

        d = self.d_r * self.smooth * 2
        self.d_image = self.image.scaled(d, d, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

        self.linePen.setWidthF(self.cm2pix * 0.75)

    # With smooth you can change quaity of bot drawing
    def checkSmooth(self):
        s = params.get("smooth")
        if self.smooth != s:
            self.smooth = s
            self.image.setDevicePixelRatio(self.smooth)

            d = self.d_r * self.smooth * 2
            self.d_image = self.image.scaled(d, d, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

    def rotate(self, angle):
        self.angle = angle

    def changeMoveDirection(self, dir):
        self.heading = dir
    
    def draw(self, qp):
        self.checkSmooth()
        self.d_center = self.d_pos + self.d_r
        p = [self.d_r / 2.71, self.d_r / 7, self.d_r / 4] # arrow points
        qp.setPen(self.linePen)

        qp.translate(self.d_center.x - self.d_r, self.d_center.y - self.d_r)
        qp.rotate(self.angle - 90)

        # Draw bot
        qp.drawImage(-self.d_r, -self.d_r, self.d_image)

        qp.rotate(self.heading + 180)

        # Draw arrow
        qp.drawLine(0, p[0], 0, 0)
        qp.drawLine(0, p[0], p[1], p[2])
        qp.drawLine(0, p[0], -p[1], p[2])

        qp.rotate(-self.heading - (self.angle - 90) - 180)
        qp.translate(-self.d_center.x + self.d_r, -self.d_center.y + self.d_r)


class Ball(GameUniformObject):

    def __init__(self):
        super().__init__()

        self.r = BALL_RADIUS

        self.linePen = QPen(RED_HIGH_ALPHA)
        self.linePen.setCapStyle(Qt.RoundCap)

    def draw(self, qp):
        qp.setBrush(RED_MED_ALPHA)
        for p in self.d_current:
            qp.setPen(self.linePen)
            qp.drawLine(p.x, p.y, self.d_pos.x, self.d_pos.y)
            qp.setPen(NO_PEN)
            qp.drawCircle(p, self.d_r * 2)
        qp.setBrush(RED)
        qp.drawCircle(self.d_pos, self.d_r * 2)

class Enemy(GameUniformObject):

    def __init__(self):
        super().__init__()

        self.r = ROBOT_RADIUS

        self.linePen = QPen(GRAY_HIGH_ALPHA)
        self.linePen.setCapStyle(Qt.RoundCap)

    def draw(self, qp):
        qp.setBrush(GRAY_MED_ALPHA)
        for p in self.d_current:
            qp.setPen(self.linePen)
            qp.drawLine(p.x, p.y, self.d_pos.x, self.d_pos.y)
            qp.setPen(NO_PEN)
            qp.drawCircle(p, self.d_r * 2)

        qp.setBrush(GRAY)
        qp.setPen(NO_PEN)
        qp.drawCircle(self.d_pos, self.d_r * 2)


class Field(QWidget):

    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.ball = Ball()
        self.enemies = [Enemy(), Enemy()]
        self.robots = [Robot(0), Robot(1)]
        self.ang = 0
        self.colormode = False
    
    def resizeEventP(self, event=""):
        self.updateSize()
        self.ball.updateSize(self)
        for enemy in self.enemies:
            enemy.updateSize(self)

        for robot in self.robots:
            robot.updateSize(self)

    def updateSize(self):
        # Caclulate maxium correct size of field
        self.height = self.window.height() - 36
        self.cm2pix = self.height / FIELD_WIDTH
        self.width = self.cm2pix * FIELD_HEIGHT

        self.move(7, 29)
        self.resize(self.width, self.height)

        self.width, self.height = self.height, self.width

        self.edge = EDGE * self.cm2pix
        self.line_width = LINE_WIDTH * self.cm2pix
        self.zone_width = ZONE_WIDTH * self.cm2pix
        self.zone_height = ZONE_HEIGHT * self.cm2pix
        self.zone_radius = ZONE_RADIUS * self.cm2pix

        self.center2point_x = CENTER_TO_POINT * self.cm2pix
        self.center2point_y = (ZONE_RADIUS / 2) * self.cm2pix
        self.point_size = POINT_SIZE * self.cm2pix

        self.goal_zone_width = GOAL_ZONE_WIDTH * self.cm2pix
        self.goal_zone_height = GOAL_ZONE_HEIGHT * self.cm2pix
        self.goal_height = GOAL_HEIGHT * self.cm2pix
        self.goal_width = GOAL_WIDTH * self.cm2pix

        self.center = Point(self.width / 2, self.height / 2)

        self.white_pen = QPen(Qt.white, self.line_width, Qt.SolidLine)
        self.black_thin_pen = QPen(Qt.black, self.line_width / 3, Qt.SolidLine)
        self.black_pen = QPen(Qt.black, self.line_width, Qt.SolidLine)
        self.black_half_pen = QPen(Qt.black, self.line_width / 1.5, Qt.SolidLine)
        if self.colormode:
            self.yellow_pen = QPen(BLUE, self.line_width / 1.3 + 2, Qt.SolidLine)
            self.blue_pen = QPen(YELLOW, self.line_width / 1.3 + 2, Qt.SolidLine)
        else:
            self.yellow_pen = QPen(YELLOW, self.line_width / 1.3 + 2, Qt.SolidLine)
            self.blue_pen = QPen(BLUE, self.line_width / 1.3 + 2, Qt.SolidLine)
        
    def paintEvent(self, event = ""):
        qp = Painter(self)
        qp.translate(self.height, 0)
        qp.rotate(90)

        # Enable antialiasing
        qp.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform, True)

        self.drawField(qp)

        for enemy in self.enemies:
            enemy.draw(qp)

        for robot in self.robots:
            robot.draw(qp)

        self.ball.draw(qp)

        self.drawGoal(qp)
        qp.end()
    
    def updateBall(self, bot, angle, distance):
        angle += self.robots[bot].angle + 180
        angle *= DEG2RAD
        bx, by = self.robots[bot].pos.x + math.cos(angle) * distance, self.robots[bot].pos.y + math.sin(angle) * distance
        self.ball.moveByIndex(bot, bx, by)
        
    def updateEnemy(self, bot, angles, distances):
        for i in range(2):
            ex, ey = self.robots[bot].pos.x + math.cos((angles[i] + self.robots[bot].angle) * DEG2RAD) * distances[i], \
                     self.robots[bot].pos.y + math.sin((angles[i] + self.robots[bot].angle) * DEG2RAD) * distances[i]
            self.enemies[i].moveByIndex(bot, ex, ey)
   
    def updateRobot(self, bot, x, y):
        bt = self.robots[bot]
        bt.move(x, y)
    
    def drawField(self, qp):
        # draw green background
        qp.setBrush(GREEN)
        qp.setPen(NO_PEN)
        qp.drawRect(0, 0, self.width, self.height)

        # Draw goal zones
        qp.setBrush(NO_BRUSH)
        qp.setPen(self.black_pen)
        qp.drawRect(self.center.x - self.zone_width / 2, self.center.y - self.goal_zone_height / 2, self.goal_zone_width, self.goal_zone_height)
        qp.drawRect(self.center.x + self.zone_width / 2 - self.goal_zone_width, self.center.y - self.goal_zone_height / 2, self.goal_zone_width, self.goal_zone_height)

        # Draw out corner
        qp.setPen(self.white_pen)
        qp.drawRect(self.edge, self.edge, self.zone_width, self.zone_height)

        # Draw center
        qp.setPen(self.black_thin_pen)
        qp.drawCircle(self.center, self.zone_radius)

        # Draw points on field
        qp.setBrush(BLACK)
        qp.setPen(NO_PEN)
        qp.drawCircle(self.center.x, self.center.y, self.point_size)
        qp.drawCircle(self.center.x - self.center2point_x, self.center.y - self.center2point_y, self.point_size)
        qp.drawCircle(self.center.x + self.center2point_x, self.center.y - self.center2point_y, self.point_size)
        qp.drawCircle(self.center.x - self.center2point_x, self.center.y + self.center2point_y, self.point_size)
        qp.drawCircle(self.center.x + self.center2point_x, self.center.y + self.center2point_y, self.point_size)

        # Draw back goals zone
        qp.setBrush(NO_BRUSH)
        p1_x = self.edge - self.goal_width
        p2_x = self.edge + self.line_width - self.line_width
        p1_y = self.center.y - self.goal_height / 2
        p2_y = self.center.y + self.goal_height / 2

        qp.setPen(self.yellow_pen)
        qp.drawLine(p1_x, p2_y, p2_x, p2_y)
        qp.drawLine(p1_x, p1_y, p1_x, p2_y)
        qp.drawLine(p1_x, p1_y, p2_x, p1_y)

        qp.setPen(self.blue_pen)
        qp.drawLine(self.width - p1_x, p2_y, self.width - p2_x, p2_y)
        qp.drawLine(self.width - p1_x, p1_y, self.width - p1_x, p2_y)
        qp.drawLine(self.width - p1_x, p1_y, self.width - p2_x, p1_y)

    def drawGoal(self, qp):
        # Draw yellow goal
        qp.setPen(self.yellow_pen)
        qp.drawLine(self.edge, self.center.y - self.goal_height / 2 + 2, self.edge, self.center.y + self.goal_height / 2 - 2)

        # Draw blue goal
        qp.setPen(self.blue_pen)
        qp.drawLine(self.width - self.edge, self.center.y - self.goal_height / 2 + 2, self.width - self.edge, self.center.y + self.goal_height / 2 - 2)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
