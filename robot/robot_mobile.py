import math
from robot.moteur import Moteur


class RobotMobile:

    _nb_robots = 0

    def __init__(self, x=0.0, y=0.0, orientation=0.0, moteur=None):
        self.__x = x
        self.__y = y
        self.__orientation = orientation
        self.moteur = moteur
        RobotMobile._nb_robots += 1

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        self.__x = value

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        self.__y = value

    @property
    def orientation(self):
        return self.__orientation

    @orientation.setter
    def orientation(self, value):
        self.__orientation = value

    def avancer(self, distance):
        self.x = self.x + distance * math.cos(self.orientation)
        self.y = self.y + distance * math.sin(self.orientation)

    def tourner(self, angle):
        self.orientation = (self.orientation + angle) % (2 * math.pi)

    def commander(self, **kwargs):
        if self.moteur is not None:
            self.moteur.commander(**kwargs)

    def mettre_a_jour(self, dt):
        if self.moteur is not None:
            self.moteur.mettre_a_jour(self, dt)

    @classmethod
    def nombre_robots(cls) -> int:
        return cls._nb_robots

    @staticmethod
    def moteur_valide(moteur):
        return isinstance(moteur, Moteur)

    def afficher(self):
        print(self)

    def __str__(self):
        return f"(x={self.x:.2f}, y={self.y:.2f}, orientation={self.orientation:.2f})"
