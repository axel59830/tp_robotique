import math

class RobotMobile:
    def __init__(self, x=0.0, y=0.0, orientation=0.0):
        self.x = x
        self.y = y
        self.orientation = orientation

    def avancer(self, distance):
        self.x = self.x + distance * math.cos(self.orientation)
        self.y = self.y + distance * math.sin(self.orientation)

    def afficher(self):
        print(f"(x={self.x:.2f}, y={self.y:.2f}, orientation={self.orientation:.2f})")