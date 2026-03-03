from abc import ABC, abstractmethod
import math

class Obstacle(ABC):

    @abstractmethod
    def collision(self, x, y, rayon_robot):
        pass

    @abstractmethod
    def dessiner(self, vue):
        pass



class ObstacleCirculaire(Obstacle):

    def __init__(self, x, y, rayon):
        self.x = x
        self.y = y
        self.rayon = rayon

    def collision(self, x_robot, y_robot, rayon_robot):
        distance = math.sqrt((self.x - x_robot)**2 + (self.y - y_robot)**2)
        return distance <= (self.rayon + rayon_robot)

    def dessiner(self, vue):
        vue.dessiner_obstacle_circulaire(self)