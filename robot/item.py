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


class ItemSoin:
    """Redonne 1 point de vie au ramassage."""
    def __init__(self, x, y, rayon=0.18):
        self.x = x
        self.y = y
        self.rayon = rayon
        self.actif = True
        self.type = "soin"
        self.vitesse_attraction = 4.0
        self.distance_attraction = 1


    def mettre_a_jour(self, dt, robot):
        dx = robot.x - self.x
        dy = robot.y - self.y
        distance = math.hypot(dx, dy)

        if 1e-6 < distance < self.distance_attraction:
            self.x += (dx / distance) * self.vitesse_attraction * dt
            self.y += (dy / distance) * self.vitesse_attraction * dt


class ItemShield:
    """Rend le robot invincible pendant 8 secondes au ramassage."""
    def __init__(self, x, y, rayon=0.18):
        self.x = x
        self.y = y
        self.rayon = rayon
        self.actif = True
        self.type = "shield"
        self.vitesse_attraction = 4.0
        self.distance_attraction = 1

    def mettre_a_jour(self, dt, robot):
        dx = robot.x - self.x
        dy = robot.y - self.y
        distance = math.hypot(dx, dy)

        if 1e-6 < distance < self.distance_attraction:
            self.x += (dx / distance) * self.vitesse_attraction * dt
            self.y += (dy / distance) * self.vitesse_attraction * dt