BAUDRATE = 115200
SERIAL_MESSAGE_LEN = 15

import math
DEG2RAD = math.pi / 180

LIGHT = 0
NIGHT = 1

NORMAL = 0
SIMULATOR = 1

FIELD_WIDTH = 243
FIELD_HEIGHT = 182

EDGE = 30
ZONE_WIDTH = 183
ZONE_HEIGHT = 122
ZONE_RADIUS = 60

GOAL_HEIGHT = 60
GOAL_WIDTH = 7.4

BALL_RADIUS = 3.5
ROBOT_RADIUS = 11

GOAL_ZONE_WIDTH = 30
GOAL_ZONE_HEIGHT = 90

BOT_COUNT = 2

GOAL_TO_POINT = 45
CENTER_TO_POINT = FIELD_WIDTH / 2 - EDGE - GOAL_TO_POINT

LINE_WIDTH = 1.5
POINT_SIZE = 1.5

SHORTCUTS = {}
SHORTCUTS["q"] = "exit"
SHORTCUTS["s"] = ["bot1 switch", "bot2 switch"]


DEFAULT_PARAMS = {}
DEFAULT_PARAMS["smooth"] = 1
DEFAULT_PARAMS["config"] = 0
DEFAULT_PARAMS["color"] = 0
DEFAULT_PARAMS["mode"] = 0
DEFAULT_PARAMS["com_update_interval"] = 300
DEFAULT_PARAMS["com0"] = 4
DEFAULT_PARAMS["com1"] = 5

__info__ = {}
__info__["smooth"] = "(real) set quality for bots drawing: <1 - low, 1 - normal, >1 - high"
__info__["config"] = "(int) set flag for clear config file: 0 - clear when start, other - don`t clear"
__info__["color"] = "(light/night) set color palette"
__info__["mode"] = "(normal/simulator) set screen mode"
__info__["com_update_interval"] = "(real) time in ms - updates interval for com list in settings"
__info__["com0"] = "port for first bot"
__info__["com1"] = "port for second bot"

aliases = {}
aliases["nightmode"] = "set color night" # nightmode
aliases["night"] = "1" # set color night
aliases["lightmode"] = "set color light" # lightmode
aliases["sunmode"] = "set color light" # sunmode
aliases["light"] = "0" # set color light
aliases["com"] = "coms" # com list
aliases["b1"] = "bot1" # b1 set COM
aliases["b2"] = "bot2" # b2 set COM
aliases["normal"] = "0" # set mode normal
aliases["simulator"] = "1" # set mode simulator


HELP_MESSAGE = \
"Now available commands: set, get, reset<br/><b>set $variable$ $value$</b>, default value 0<br/>\
<b>get $variable$</b>, get variable value<br/>\
<b>reset $variable$</b>, set variable default value<br/>\
<br/>Now available variables:<br/>"

PARAMS_LIST = []
for key in DEFAULT_PARAMS:
    HELP_MESSAGE += key + " - " + __info__[key] + "<br/>"
    PARAMS_LIST.append(key)

HELP_MESSAGE += "Also you can use commands like 'a' for get value of a and 'a=b' for set value of a to b"
