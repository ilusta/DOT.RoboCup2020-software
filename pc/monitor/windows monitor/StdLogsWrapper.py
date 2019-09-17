
class StdLogsWrapper:

    def __init__(self, logs):
        self.log = logs.info
        self.warn = logs.warn
        self.error = logs.error
        self.text = logs.output
        self.complete = logs.complete

    def write(self, s):
        s = s.rstrip().strip()
        if len(s) > 3 and s[0] == "$" and s[2] == "$":
            cmd = s[1]
            cs = s[3:]

            if cmd == "l": self.log(cs)
            elif cmd == "w": self.warn(cs)
            elif cmd == "e": self.error(cs)
            elif cmd == "t": self.text(cs)
            elif cmd == "c": self.complete(cs)
            else: self.log(cs)
        elif len(s) > 0:
            self.log(s)

    def flush(self, *args, **kwargs):
        pass
