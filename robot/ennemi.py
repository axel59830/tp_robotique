import math


class Ennemi:

    def __init__(self, x, y, vitesse=1.0, rayon=0.3):
        self.x = x
        self.y = y
        self.vitesse = vitesse
        self.rayon = rayon
        self.cooldown = 0.0

    def mettre_a_jour(self, dt, robot, environnement):

        # direction vers le robot
        dx = robot.x - self.x
        dy = robot.y - self.y
        distance = math.hypot(dx, dy)

        if distance > 1e-6:
            self.x += (dx / distance) * self.vitesse * dt
            self.y += (dy / distance) * self.vitesse * dt

        # tir
        self.cooldown -= dt
        if self.cooldown <= 0:
            self.tirer(robot, environnement)
            self.cooldown = 2.0  # tire toutes les 2 secondes

    def tirer(self, robot, environnement):
        from robot.projectile import Projectile

        dx = robot.x - self.x
        dy = robot.y - self.y
        distance = math.hypot(dx, dy)

        if distance == 0:
            return

        vx = (dx / distance) * 3.0
        vy = (dy / distance) * 3.0

        projectile = Projectile(self.x, self.y, vx, vy)
        environnement.ajouter_projectile(projectile)