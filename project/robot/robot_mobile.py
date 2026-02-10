import math

class RobotMobile:
    def __init__(self, x=0.0, y=0.0, theta=0.0):
        self.x = float(x)
        self.y = float(y)
        self.theta = float(theta)

    def position(self):
        return self.x, self.y

    def afficher(self):
        print(self.x, self.y, self.theta)

    def avancer(self, distance):
        self.x += distance * math.cos(self.theta)
        self.y += distance * math.sin(self.theta)
