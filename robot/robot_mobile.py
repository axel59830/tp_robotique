import math
from robot.moteur import Moteur


class RobotMobile:
    _nb_robots = 0

    def __init__(self, x=0.0, y=0.0, orientation=0.0, moteur=None, rayon=0.3, vie_max=5):
        self.__x = x
        self.__y = y
        self.__orientation = orientation
        self.moteur = moteur

        self.rayon = rayon
        self.vie_max = vie_max
        self.vie = vie_max

        self.cooldown_tir = 0.0
        self.cadence_tir = 0.25

        self.cooldown_degats = 0.0
        self.temps_invulnerable = 0.6

        # Shield
        self.shield_actif = False
        self.shield_duree = 0.0

        # progression
        self.niveau = 1
        self.experience = 0
        self.experience_pour_niveau_suivant = 5

        # stats améliorables
        self.bonus_vitesse = 0.0
        self.degats_projectile = 1
        self.taille_projectile = 0.10
        self.vitesse_projectile = 7.0

        RobotMobile._nb_robots += 1

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        self.__x = value

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        self.__y = value

    @property
    def orientation(self):
        return self.__orientation

    @orientation.setter
    def orientation(self, value):
        self.__orientation = value

    def avancer(self, distance):
        self.x = self.x + distance * math.cos(self.orientation)
        self.y = self.y + distance * math.sin(self.orientation)

    def tourner(self, angle):
        self.orientation = (self.orientation + angle) % (2 * math.pi)

    def commander(self, **kwargs):
        if self.moteur is not None:
            self.moteur.commander(**kwargs)

    def mettre_a_jour(self, dt):
        if self.moteur is not None:
            self.moteur.mettre_a_jour(self, dt)

        if self.cooldown_tir > 0:
            self.cooldown_tir -= dt

        if self.cooldown_degats > 0:
            self.cooldown_degats -= dt

        if self.shield_actif:
            self.shield_duree -= dt
            if self.shield_duree <= 0:
                self.shield_actif = False
                self.shield_duree = 0.0

    def peut_tirer(self):
        return self.cooldown_tir <= 0.0

    def tirer(self):
        self.cooldown_tir = self.cadence_tir

    def peut_subir_degats(self):
        # Invincible si shield actif OU en cooldown normal
        if self.shield_actif:
            return False
        return self.cooldown_degats <= 0.0

    def subir_degats(self, degats):
        if self.peut_subir_degats():
            self.vie -= degats
            self.cooldown_degats = self.temps_invulnerable

    def activer_shield(self, duree=10.0):
        self.shield_actif = True
        self.shield_duree = duree

    def est_vivant(self):
        return self.vie > 0

    def ajouter_experience(self, quantite):
        self.experience += quantite
        return self.verifier_montee_niveau()

    def verifier_montee_niveau(self):
        montee = False
        while self.experience >= self.experience_pour_niveau_suivant:
            self.experience -= self.experience_pour_niveau_suivant
            self.niveau += 1
            self.experience_pour_niveau_suivant = int(self.experience_pour_niveau_suivant * 1.4) + 2
            montee = True
        return montee

    def soigner(self, quantite):
        self.vie = min(self.vie_max, self.vie + quantite)

    def appliquer_amelioration(self, nom):
        if nom == "cadence":
            self.cadence_tir = max(0.08, self.cadence_tir - 0.03)
        elif nom == "vitesse":
            self.bonus_vitesse += 0.4
        elif nom == "vitalite":
            self.vie_max += 1
            self.vie += 1
        elif nom == "degats":
            self.degats_projectile += 1
        elif nom == "taille":
            self.taille_projectile += 0.03
        elif nom == "projectile_speed":
            self.vitesse_projectile += 1.0

    def reinitialiser(self):
        self.x = 0.0
        self.y = 0.0
        self.orientation = 0.0

        self.vie_max = 5
        self.vie = self.vie_max

        self.cooldown_tir = 0.0
        self.cadence_tir = 0.25

        self.cooldown_degats = 0.0
        self.temps_invulnerable = 0.6

        self.shield_actif = False
        self.shield_duree = 0.0

        self.niveau = 1
        self.experience = 0
        self.experience_pour_niveau_suivant = 5

        self.bonus_vitesse = 0.0
        self.degats_projectile = 1
        self.taille_projectile = 0.10
        self.vitesse_projectile = 7.0

    @classmethod
    def nombre_robots(cls) -> int:
        return cls._nb_robots

    @staticmethod
    def moteur_valide(moteur):
        return isinstance(moteur, Moteur)

    def afficher(self):
        print(self)

    def __str__(self):
        return f"(x={self.x:.2f}, y={self.y:.2f}, orientation={self.orientation:.2f})"