import math
from robot.projectile import Projectile


class Ennemi:
    def __init__(self, x, y, vitesse=1.0, rayon=0.3, vie=2):
        self.x = x
        self.y = y
        self.vitesse = vitesse
        self.rayon = rayon
        self.vie = vie
        self.actif = True
        self.cooldown = 1.5

    def mettre_a_jour(self, dt, robot, environnement):
        dx = robot.x - self.x
        dy = robot.y - self.y
        distance = math.hypot(dx, dy)

        if distance > 2.5 and distance > 1e-6:
            self.x += (dx / distance) * self.vitesse * dt
            self.y += (dy / distance) * self.vitesse * dt

        self.cooldown -= dt
        if self.cooldown <= 0:
            self.tirer(robot, environnement)
            self.cooldown = 1.8

    def tirer(self, robot, environnement):
        dx = robot.x - self.x
        dy = robot.y - self.y
        distance = math.hypot(dx, dy)

        if distance <= 1e-6:
            return

        vitesse_proj = 1.8          
        vx = (dx / distance) * vitesse_proj
        vy = (dy / distance) * vitesse_proj

        projectile = Projectile(
            self.x,
            self.y,
            vx,
            vy,
            rayon=0.1,
            owner="ennemi",
            degats=1,
            duree_vie=5.0           
        )
        environnement.ajouter_projectile(projectile)

    def subir_degats(self, degats):
        self.vie -= degats
        if self.vie <= 0:
            self.actif = False