import math
import random


class RayonLaser:
    """
    Laser instantané : tire un rayon dans la direction du robot,
    touche TOUS les ennemis alignés dans un cône très étroit.
    Proc toutes les 5 secondes.
    """
    NOM = "laser"
    LABEL = "⚡ Laser"
    DESCRIPTION = "Rayon instantané toutes les 5s qui traverse tous les ennemis"
    COOLDOWN_MAX = 5.0

    def __init__(self):
        self.cooldown = 0.0
        self.actif = True
        # Animation : durée d'affichage du rayon
        self.flash_duree = 0.0
        self.flash_max = 0.15

    def mettre_a_jour(self, dt, robot, environnement):
        if self.cooldown > 0:
            self.cooldown -= dt
        if self.flash_duree > 0:
            self.flash_duree -= dt

        if self.cooldown <= 0:
            self.declencher(robot, environnement)
            self.cooldown = self.COOLDOWN_MAX
            self.flash_duree = self.flash_max

    def declencher(self, robot, environnement):
        """Touche tous les ennemis dans la direction du robot (cône étroit)."""
        angle = robot.orientation
        portee = 20.0          # traverse tout le terrain
        largeur_cone = 0.25    # demi-angle en radians (~14°)

        tous = (
            [e for e in environnement.ennemis if e.actif] +
            [e for e in environnement.ennemis_nuls if e.actif]
        )
        for ennemi in tous:
            dx = ennemi.x - robot.x
            dy = ennemi.y - robot.y
            dist = math.hypot(dx, dy)
            if dist < 1e-6 or dist > portee:
                continue
            angle_ennemi = math.atan2(dy, dx)
            diff = abs(_normaliser_angle(angle_ennemi - angle))
            if diff < largeur_cone:
                ennemi.subir_degats(3)
                if not ennemi.actif:
                    environnement.score += 20 if ennemi in environnement.ennemis else 10
                    environnement.faire_tomber_xp(ennemi.x, ennemi.y,
                                                  valeur=2 if ennemi in environnement.ennemis else 1)
                    environnement.faire_tomber_item_bonus(ennemi.x, ennemi.y)

    @property
    def ratio_cooldown(self):
        return max(0.0, 1.0 - self.cooldown / self.COOLDOWN_MAX)

    @property
    def en_flash(self):
        return self.flash_duree > 0


class LanceFlammes:
    """
    Lance-flammes en zone : explose en cercle autour du robot,
    inflige des dégâts à tous les ennemis dans le rayon.
    Proc toutes les 8 secondes.
    """
    NOM = "lance_flammes"
    LABEL = "🔥 Lance-flammes"
    DESCRIPTION = "Explosion de feu en zone autour du robot toutes les 8s"
    COOLDOWN_MAX = 8.0
    RAYON_EXPLOSION = 2.5

    def __init__(self):
        self.cooldown = 0.0
        self.actif = True
        # Animation d'explosion
        self.explosion_duree = 0.0
        self.explosion_max = 0.4

    def mettre_a_jour(self, dt, robot, environnement):
        if self.cooldown > 0:
            self.cooldown -= dt
        if self.explosion_duree > 0:
            self.explosion_duree -= dt

        if self.cooldown <= 0:
            self.declencher(robot, environnement)
            self.cooldown = self.COOLDOWN_MAX
            self.explosion_duree = self.explosion_max

    def declencher(self, robot, environnement):
        """Inflige des dégâts à tous les ennemis dans le rayon."""
        tous = (
            [e for e in environnement.ennemis if e.actif] +
            [e for e in environnement.ennemis_nuls if e.actif]
        )
        for ennemi in tous:
            dist = math.hypot(ennemi.x - robot.x, ennemi.y - robot.y)
            if dist <= self.RAYON_EXPLOSION:
                ennemi.subir_degats(2)
                if not ennemi.actif:
                    environnement.score += 20 if ennemi in environnement.ennemis else 10
                    environnement.faire_tomber_xp(ennemi.x, ennemi.y,
                                                  valeur=2 if ennemi in environnement.ennemis else 1)
                    environnement.faire_tomber_item_bonus(ennemi.x, ennemi.y)

    @property
    def ratio_cooldown(self):
        return max(0.0, 1.0 - self.cooldown / self.COOLDOWN_MAX)

    @property
    def en_explosion(self):
        return self.explosion_duree > 0


def _normaliser_angle(a):
    while a > math.pi:
        a -= 2 * math.pi
    while a < -math.pi:
        a += 2 * math.pi
    return a
