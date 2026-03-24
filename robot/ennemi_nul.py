import math


class Ennemi_nul:
    def __init__(self, x, y, vitesse=1.6, rayon=0.28, vie=1, degats_contact=1):
        self.x = x
        self.y = y
        self.vitesse = vitesse
        self.rayon = rayon
        self.vie = vie
        self.degats_contact = degats_contact
        self.actif = True

    def mettre_a_jour(self, dt, robot, environnement):
        dx = robot.x - self.x
        dy = robot.y - self.y
        distance = math.hypot(dx, dy)

        if distance > 1e-6:
            self.x += (dx / distance) * self.vitesse * dt
            self.y += (dy / distance) * self.vitesse * dt

    def subir_degats(self, degats):
        self.vie -= degats
        if self.vie <= 0:
            self.actif = False