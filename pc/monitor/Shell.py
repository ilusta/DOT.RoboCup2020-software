from Constants import *
from Params import Params
from StdLogsWrapper import *
from Tools import *

import sys

class Shell:
    def __new__(cls, writer = lambda x: 0): # Singleton
        if not hasattr(cls, 'instance'):
            cls.instance = super(Shell, cls).__new__(cls)
        return cls.instance

    def __init__(self, writer = lambda x: 0):
        self.params = Params()
        self.writer = writer

    def run(self, cmd, fcmd = ""):
        if len(cmd) == 0 and len(fcmd) == 0:
            return
        if cmd[0] == "!":
            symbol = cmd[1]
            index = int(cmd[3])
            self.writer(symbol, index)
            return
            
        cmds = [c for c in cmd.strip().split(' ') if not c == " "]

        # Check aliases
        haveAlias = False
        for el in range(len(cmds)):
            if cmds[el] in aliases.keys():
                cmds[el] = str(aliases[cmds[el]])
                haveAlias = True

        if haveAlias:
            try:
                return self.run(" ".join(cmds), fcmd)
            except RecursionError:
                l_error("Cyclic alias link detected")
                return
        else:
            fcmd = cmd

        # Check short commands -> hard aliases
        if cmd.count("=") == 1: # Set variable by "$variable$ = $value$"
            splitted = cmd.split("=")
            return self.run("set {} {}".format(splitted[0].strip(), splitted[1].strip()))

        elif cmds[0] == "help": # Help command
            l_text("~:>> " + fcmd)
            l_text(HELP_MESSAGE)
            return

        elif cmds[0] == "exit" or cmds[0] == "quit" or cmd == "q":
            sys.exit()

        elif len(cmds) == 1: # Get variable value by name
            return self.run("get {}".format(cmds[0]))

        l_text("~:>> " + fcmd)

        # Normal commands
        if cmds[0] == "set":
            if len(cmds) == 1:
                l_error("No specified variable name")
                return
            if not cmds[1] in list(DEFAULT_PARAMS.keys()):
                l_warn("{} variable not used in program".format(cmds[1]))
                return
            if len(cmds) == 2:
                if self.params.get(cmds[1]) == 1.0:
                    l_warn("{} also is 1".format(cmds[1]))
                else:
                    self.params.set(cmds[1], 1)
                    l_complete("Value of {} updated to placeholder 1".format(cmds[1]))
            else:
                if not isNumber(cmds[2]):
                    l_error("Value of variable not a number!")
                elif self.params.get(cmds[1]) == float(cmds[2]):
                    l_warn("{} also is {}".format(cmds[1], cmds[2]))
                else:
                    self.params.set(cmds[1], cmds[2])
                    l_complete("Value of {} updated to {}".format(cmds[1], cmds[2]))

        elif cmds[0] == "get":
            if len(cmds) == 1:
                l_error("No specified variable name")
                return
            if not cmds[1] in list(DEFAULT_PARAMS.keys()):
                l_warn("{} variable doesn`t exist".format(cmds[1]))
                return
            l_log("{} == {}".format(cmds[1], self.params.get(cmds[1])))

        elif cmds[0] == "reset":
            if len(cmds) == 1:
                l_error("No specified variable name")
                return
            if not cmds[1] in list(DEFAULT_PARAMS.keys()):
                l_warn("{} variable doesn`t exist".format(cmds[1]))
                return
            v = DEFAULT_PARAMS[cmds[1]]
            self.params.set(cmds[1], v)
            l_log("Reset value of variable {} to {}".format(cmds[1], v))

        elif len(cmds[0]) == 4 and cmds[0][:3] == "bot":
            if len(cmds) != 3:
                l_error("Bad command")
                return

        else:
            l_error("Not supported command")