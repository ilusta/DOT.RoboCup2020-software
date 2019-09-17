class Point:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def move(self, x, y):
        self.x += x
        self.y += y

    def set(self, x, y):
        self.x = x
        self.y = y

    def reset(self):
        self.x = 0
        self.y = 0

    def toCoord(self):
        return self.x, self.y

    def copy(self):
        return Point(self.x, self.y)

    def __add__(self, p):
        if type(p) is Point:
            return Point(self.x + p.x, self.y + p.y)
        elif type(p) is int or type(p) is float:
            return Point(self.x + p, self.y + p)
        else:
            raise TypeError("Unsupported type")

    def __mul__(self, p):
        if type(p) is Point:
            return Point(self.x * p.x, self.y * p.y)
        elif type(p) is int or type(p) is float:
            return Point(self.x * p, self.y * p)
        else:
            raise TypeError("Unsupported type")

    def __truediv__(self, p):
        if type(p) is Point:
            return Point(self.x / p.x, self.y / p.y)
        elif type(p) is int or type(p) is float:
            return Point(self.x / p, self.y / p)
        else:
            raise TypeError("Unsupported type")

    def __eq__(self, p):
        if type(p) is Point:
            return self.x == p.x and self.y == p.y
        elif type(p) is int or type(p) is float:
            return self.x == p and self.y == p
        else:
            raise TypeError("Unsupported type")
