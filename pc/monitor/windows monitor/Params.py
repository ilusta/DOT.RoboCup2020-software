import csv
import os
from pathlib import Path

from Constants import *
from StdLogsWrapper import *
from Tools import *

class Params:
    def __init__(self):
        self.path = "config.csv"

        if not (os.path.exists(self.path) and os.path.isfile(self.path)):
            Path(self.path).touch()

        if self.get("config", False) == 0:
            os.remove(self.path)
            Path(self.path).touch()

    def get(self, name, suspendErrors = False):
        gotIt = False
        with open(self.path, "r") as inf:
            reader = csv.reader(inf.readlines(), delimiter='=')

            for line in reader:
                if len(line) != 2:
                    if not suspendErrors:
                        l_error("ilusta error -> {}".format(str(line)))
                    continue

                if line[0] == name:
                    if isNumber(line[1]):
                        ans = float(line[1])
                    else:
                        l_error("Bad value {} of variable {} - using default".format(line[1], line[0]))
                        ans = DEFAULT_PARAMS[name]
                    gotIt = True
                    break

        if gotIt:
            return ans
        else:
            return DEFAULT_PARAMS[name]

    def set(self, name, value):
        gotIt = False

        with open(self.path, "r") as inf:
            reader = csv.reader(inf.readlines(), delimiter='=')

        with open(self.path, 'w', newline='') as outf:
            writer = csv.writer(outf, delimiter='=')
            for line in reader:
                if line[0] == name:
                    writer.writerow([name, value])
                    gotIt = True
                    break
                else:
                    writer.writerow(line)
            if not gotIt:
                writer.writerow([name, value])
