import math


class ItemExperience:
    def __init__(self, x, y, valeur=1, rayon=0.14):
        self.x = x
        self.y = y
        self.valeur = valeur
        self.rayon = rayon
        self.actif = True
        self.vitesse_attraction = 4.0
        self.distance_attraction = 1.6

    def mettre_a_jour(self, dt, robot):
        dx = robot.x - self.x
        dy = robot.y - self.y
        distance = math.hypot(dx, dy)

        if 1e-6 < distance < self.distance_attraction:
            self.x += (dx / distance) * self.vitesse_attraction * dt
            self.y += (dy / distance) * self.vitesse_attraction * dt