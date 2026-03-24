class Projectile:
    def __init__(self, x, y, vx, vy, rayon=0.1, owner="joueur", degats=1, duree_vie=3.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.rayon = rayon
        self.owner = owner
        self.degats = degats
        self.duree_vie = duree_vie
        self.actif = True

    def mettre_a_jour(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.duree_vie -= dt

        if self.duree_vie <= 0:
            self.actif = False