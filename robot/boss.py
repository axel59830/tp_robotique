import math


class Boss:
    """
    Boss de vague 10 (et multiples de 10).
    - Très lent, ne tire pas
    - Beaucoup de points de vie
    - Dégâts au contact élevés
    - Barre de vie affichée
    """
    def __init__(self, x, y, vague=10):
        self.x = x
        self.y = y
        # Vie scale avec la vague (boss de vague 20 est plus dur)
        facteur = max(1, (vague // 10))
        self.vie_max = 80 * facteur
        self.vie = self.vie_max
        self.vitesse = 0.45
        self.rayon = 0.7
        self.degats_contact = 2
        self.actif = True
        self.cooldown_contact = 0.0  # évite les dégâts en rafale au contact

    def mettre_a_jour(self, dt, robot, environnement):
        dx = robot.x - self.x
        dy = robot.y - self.y
        distance = math.hypot(dx, dy)

        if distance > 1e-6:
            self.x += (dx / distance) * self.vitesse * dt
            self.y += (dy / distance) * self.vitesse * dt

        if self.cooldown_contact > 0:
            self.cooldown_contact -= dt

    def subir_degats(self, degats):
        self.vie -= degats
        if self.vie <= 0:
            self.vie = 0
            self.actif = False

    @property
    def ratio_vie(self):
        return self.vie / self.vie_max if self.vie_max > 0 else 0.0
