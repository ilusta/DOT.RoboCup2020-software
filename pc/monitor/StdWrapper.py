
class StdWrapper:
    def __init__(self, func):
        self.f = func

    def write(self, s):
        s = s.rstrip().strip()
        if len(s) > 1: self.f(s)

    def flush(self, *args, **kwargs):
        pass
