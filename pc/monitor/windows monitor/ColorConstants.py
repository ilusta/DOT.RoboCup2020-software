from PyQt5.QtGui import QBrush, QColor, QIcon
from PyQt5.QtCore import Qt

WHITE = QColor(255, 255, 255)
BLACK = QColor(0, 0, 0)
BLUE = QColor(30, 144, 255)
YELLOW = QColor(212, 175, 55)
GREEN = QColor(0, 105, 50)

TRUE_RED = QColor(255, 0, 0)
RED = QColor(200, 50, 50)
RED_HIGH_ALPHA = QColor(200, 50, 50, 128)
RED_MED_ALPHA = QColor(200, 50, 50, 180)

GRAY = QColor(50, 50, 50)
GRAY_HIGH_ALPHA = QColor(80, 80, 80, 128)
GRAY_MED_ALPHA = QColor(50, 50, 50, 200)

NO_BRUSH = QBrush(Qt.black, Qt.NoBrush)
NO_PEN = Qt.NoPen

NO_ICON = QIcon()
TRIGGER_ICON = QIcon("images/triggerIcon.svg")
