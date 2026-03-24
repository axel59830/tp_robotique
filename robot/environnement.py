import math
import random
from robot.projectile import Projectile
from robot.ennemi import Ennemi
from robot.ennemi_nul import Ennemi_nul
from robot.item import ItemExperience


class Environnement:

    def __init__(self, largeur=10, hauteur=10):
        self.largeur = largeur
        self.hauteur = hauteur
        self.robot = None
        self.obstacles = []
        self.ennemis = []
        self.ennemis_nuls = []
        self.projectiles = []
        self.items = []

        self.vague = 0
        self.score = 0
        self.game_over = False

        self.attente_prochaine_vague = False
        self.temps_avant_prochaine_vague = 0.0

        self.en_pause_upgrade = False
        self.choix_ameliorations = []

    def ajouter_robot(self, robot):
        self.robot = robot

    def ajouter_obstacle(self, obstacle):
        self.obstacles.append(obstacle)

    def ajouter_ennemi(self, ennemi):
        self.ennemis.append(ennemi)

    def ajouter_ennemi_nul(self, ennemi_nul):
        self.ennemis_nuls.append(ennemi_nul)

    def ajouter_projectile(self, projectile):
        self.projectiles.append(projectile)

    def ajouter_item(self, item):
        self.items.append(item)

    def reinitialiser(self):
        self.ennemis.clear()
        self.ennemis_nuls.clear()
        self.projectiles.clear()
        self.items.clear()

        self.vague = 0
        self.score = 0
        self.game_over = False
        self.attente_prochaine_vague = False
        self.temps_avant_prochaine_vague = 0.0
        self.en_pause_upgrade = False
        self.choix_ameliorations = []

        if self.robot is not None:
            self.robot.reinitialiser()

        self.lancer_vague_suivante()

    def lancer_vague_suivante(self):
        self.vague += 1
        total_ennemis = self.vague

        nb_tireurs = self.vague // 4
        if nb_tireurs > total_ennemis:
            nb_tireurs = total_ennemis

        nb_contact = total_ennemis - nb_tireurs

        for _ in range(nb_contact):
            x, y = self.position_spawn()
            self.ajouter_ennemi_nul(Ennemi_nul(x, y, vitesse=1.4 + 0.05 * self.vague))

        for _ in range(nb_tireurs):
            x, y = self.position_spawn()
            self.ajouter_ennemi(Ennemi(x, y, vitesse=0.9 + 0.03 * self.vague))

        self.attente_prochaine_vague = False
        self.temps_avant_prochaine_vague = 0.0

    def position_spawn(self):
        marge = 0.8
        cote = random.choice(["haut", "bas", "gauche", "droite"])

        if cote == "haut":
            x = random.uniform(-self.largeur / 2 + marge, self.largeur / 2 - marge)
            y = self.hauteur / 2 - marge
        elif cote == "bas":
            x = random.uniform(-self.largeur / 2 + marge, self.largeur / 2 - marge)
            y = -self.hauteur / 2 + marge
        elif cote == "gauche":
            x = -self.largeur / 2 + marge
            y = random.uniform(-self.hauteur / 2 + marge, self.hauteur / 2 - marge)
        else:
            x = self.largeur / 2 - marge
            y = random.uniform(-self.hauteur / 2 + marge, self.hauteur / 2 - marge)

        return x, y

    def generer_choix_ameliorations(self):
        pool = [
            ("cadence", "Cadence de tir"),
            ("vitesse", "Vitesse"),
            ("vitalite", "Vitalité"),
            ("degats", "Dégâts"),
            ("taille", "Taille projectile"),
            ("projectile_speed", "Vitesse projectile"),
        ]
        self.choix_ameliorations = random.sample(pool, k=3)

    def appliquer_choix_amelioration(self, index):
        if not self.en_pause_upgrade:
            return

        if index < 0 or index >= len(self.choix_ameliorations):
            return

        nom, _ = self.choix_ameliorations[index]
        self.robot.appliquer_amelioration(nom)

        self.en_pause_upgrade = False
        self.choix_ameliorations = []

    def mettre_a_jour(self, dt, tirer_joueur=False, choix_upgrade=None):
        if self.robot is None:
            return

        if self.game_over:
            return

        if self.en_pause_upgrade:
            if choix_upgrade is not None:
                self.appliquer_choix_amelioration(choix_upgrade - 1)
            return

        old_x = self.robot.x
        old_y = self.robot.y
        old_orientation = self.robot.orientation

        self.robot.mettre_a_jour(dt)

        demi_l = self.largeur / 2
        demi_h = self.hauteur / 2
        self.robot.x = max(-demi_l + self.robot.rayon, min(demi_l - self.robot.rayon, self.robot.x))
        self.robot.y = max(-demi_h + self.robot.rayon, min(demi_h - self.robot.rayon, self.robot.y))

        for obs in self.obstacles:
            if obs.collision(self.robot.x, self.robot.y, self.robot.rayon):
                self.robot.x = old_x
                self.robot.y = old_y
                self.robot.orientation = old_orientation
                break

        if tirer_joueur and self.robot.peut_tirer():
            self.tirer_joueur()

        for ennemi in self.ennemis:
            ennemi.mettre_a_jour(dt, self.robot, self)

        for ennemi_nul in self.ennemis_nuls:
            ennemi_nul.mettre_a_jour(dt, self.robot, self)

        for projectile in self.projectiles:
            projectile.mettre_a_jour(dt)

        for item in self.items:
            item.mettre_a_jour(dt, self.robot)

        marge = 1.0
        for projectile in self.projectiles:
            if (projectile.x < -demi_l - marge or projectile.x > demi_l + marge or
                    projectile.y < -demi_h - marge or projectile.y > demi_h + marge):
                projectile.actif = False

        self.gerer_collisions()

        self.ennemis = [e for e in self.ennemis if e.actif]
        self.ennemis_nuls = [e for e in self.ennemis_nuls if e.actif]
        self.projectiles = [p for p in self.projectiles if p.actif]
        self.items = [i for i in self.items if i.actif]

        if not self.robot.est_vivant():
            self.game_over = True
            return

        if len(self.ennemis) == 0 and len(self.ennemis_nuls) == 0:
            if not self.attente_prochaine_vague:
                self.attente_prochaine_vague = True
                self.temps_avant_prochaine_vague = 3.0
            else:
                self.temps_avant_prochaine_vague -= dt
                if self.temps_avant_prochaine_vague <= 0:
                    self.lancer_vague_suivante()

    def tirer_joueur(self):
        angle = self.robot.orientation
        vitesse_proj = self.robot.vitesse_projectile

        offset = self.robot.rayon + 0.12
        x = self.robot.x + math.cos(angle) * offset
        y = self.robot.y + math.sin(angle) * offset
        vx = math.cos(angle) * vitesse_proj
        vy = math.sin(angle) * vitesse_proj

        projectile = Projectile(
            x=x,
            y=y,
            vx=vx,
            vy=vy,
            rayon=self.robot.taille_projectile,
            owner="joueur",
            degats=self.robot.degats_projectile,
            duree_vie=2.0
        )
        self.ajouter_projectile(projectile)
        self.robot.tirer()

    def faire_tomber_xp(self, x, y, valeur=1):
        self.ajouter_item(ItemExperience(x, y, valeur=valeur))

    def gerer_collisions(self):
        for ennemi_nul in self.ennemis_nuls:
            if self.collision_cercles(
                self.robot.x, self.robot.y, self.robot.rayon,
                ennemi_nul.x, ennemi_nul.y, ennemi_nul.rayon
            ):
                self.robot.subir_degats(ennemi_nul.degats_contact)

        for ennemi in self.ennemis:
            if self.collision_cercles(
                self.robot.x, self.robot.y, self.robot.rayon,
                ennemi.x, ennemi.y, ennemi.rayon
            ):
                self.robot.subir_degats(1)

        for projectile in self.projectiles:
            if not projectile.actif:
                continue

            if projectile.owner == "ennemi":
                if self.collision_cercles(
                    self.robot.x, self.robot.y, self.robot.rayon,
                    projectile.x, projectile.y, projectile.rayon
                ):
                    self.robot.subir_degats(projectile.degats)
                    projectile.actif = False

            elif projectile.owner == "joueur":
                for ennemi_nul in self.ennemis_nuls:
                    if ennemi_nul.actif and self.collision_cercles(
                        ennemi_nul.x, ennemi_nul.y, ennemi_nul.rayon,
                        projectile.x, projectile.y, projectile.rayon
                    ):
                        ennemi_nul.subir_degats(projectile.degats)
                        projectile.actif = False
                        if not ennemi_nul.actif:
                            self.score += 10
                            self.faire_tomber_xp(ennemi_nul.x, ennemi_nul.y, valeur=1)
                        break

                if not projectile.actif:
                    continue

                for ennemi in self.ennemis:
                    if ennemi.actif and self.collision_cercles(
                        ennemi.x, ennemi.y, ennemi.rayon,
                        projectile.x, projectile.y, projectile.rayon
                    ):
                        ennemi.subir_degats(projectile.degats)
                        projectile.actif = False
                        if not ennemi.actif:
                            self.score += 20
                            self.faire_tomber_xp(ennemi.x, ennemi.y, valeur=2)
                        break

        for item in self.items:
            if item.actif and self.collision_cercles(
                self.robot.x, self.robot.y, self.robot.rayon,
                item.x, item.y, item.rayon
            ):
                item.actif = False
                montee = self.robot.ajouter_experience(item.valeur)
                if montee:
                    self.en_pause_upgrade = True
                    self.generer_choix_ameliorations()

    @staticmethod
    def collision_cercles(x1, y1, r1, x2, y2, r2):
        dx = x1 - x2
        dy = y1 - y2
        return (dx * dx + dy * dy) <= (r1 + r2) ** 2