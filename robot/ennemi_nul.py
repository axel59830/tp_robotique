import math


class Ennemi_nul:

    def __init__(self, x, y, vitesse=1.5, rayon=0.3):
        self.x = x
        self.y = y
        self.vitesse = vitesse
        self.rayon = rayon
        self.cooldown = 0.0

    def mettre_a_jour(self, dt, robot, environnement):

        dx = robot.x - self.x
        dy = robot.y - self.y
        distance = math.hypot(dx, dy)

        if distance > 1e-6:
            self.x += (dx / distance) * self.vitesse * dt
            self.y += (dy / distance) * self.vitesse * dt

        