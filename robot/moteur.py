from abc import ABC, abstractmethod
from math import cos, sin


class Moteur(ABC):

    @abstractmethod
    def commander(self, *args, **kwargs):
        pass

    @abstractmethod
    def mettre_a_jour(self, robot, dt):
        pass


class MoteurDifferentiel(Moteur):

    def __init__(self, v=0.0, omega=0.0):
        self.v = v
        self.omega = omega

    def commander(self, v, omega):
        self.v = v
        self.omega = omega

    def mettre_a_jour(self, robot, dt):
        theta = robot.orientation
        robot.orientation = theta + self.omega * dt
        robot.x = robot.x + self.v * cos(theta) * dt
        robot.y = robot.y + self.v * sin(theta) * dt


class MoteurOmnidirectionnel(Moteur):

    def __init__(self, vx=0.0, vy=0.0, omega=0.0):
        self.vx = vx
        self.vy = vy
        self.omega = omega

    def commander(self, vx, vy, omega):
        self.vx = vx
        self.vy = vy
        self.omega = omega

    def mettre_a_jour(self, robot, dt):
        theta = robot.orientation
        robot.orientation = theta + self.omega * dt
        robot.x = robot.x + (self.vx * cos(theta) - self.vy * sin(theta)) * dt
        robot.y = robot.y + (self.vx * sin(theta) + self.vy * cos(theta)) * dt
