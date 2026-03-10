class Projectile:
    
    def __init__(self, x, y, vx, vy, rayon=0.1):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.rayon = rayon
        self.actif = True

    def mettre_a_jour(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt