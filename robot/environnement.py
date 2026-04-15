import math
import random
from robot.projectile import Projectile
from robot.ennemi import Ennemi
from robot.ennemi_nul import Ennemi_nul
from robot.boss import Boss
from robot.item import ItemExperience, ItemSoin, ItemShield
from robot.zone_capturable import ZoneCapturable
from robot.robot_allie import RobotAllie


class Environnement:

    def __init__(self, largeur=30, hauteur=30):
        self.largeur = largeur
        self.hauteur = hauteur
        self.robot = None
        self.robot_allie = None
        self.zone_capturable = None
        self.obstacles = []
        self.ennemis = []
        self.ennemis_nuls = []
        self.boss = None          # boss actif (None si pas de boss)
        self.projectiles = []
        self.items = []

        self.vague = 0
        self.score = 0
        self.game_over = False

        self.attente_prochaine_vague = False
        self.temps_avant_prochaine_vague = 0.0

        self.en_pause_upgrade = False
        self.choix_ameliorations = []

        self.en_pause_arme = False
        self.choix_armes = []

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
        self.boss = None

        self.vague = 0
        self.score = 0
        self.game_over = False
        self.attente_prochaine_vague = False
        self.temps_avant_prochaine_vague = 0.0
        self.en_pause_upgrade = False
        self.choix_ameliorations = []
        self.en_pause_arme = False
        self.choix_armes = []

        if self.robot is not None:
            self.robot.reinitialiser()

        self.lancer_vague_suivante()

    def lancer_vague_suivante(self):
        self.vague += 1

        # Vague 8 : créer une zone capturable
        if self.vague == 8 and self.zone_capturable is None:
            # Créer la zone capturable près du centre
            x = random.uniform(-5, 5)
            y = random.uniform(-5, 5)
            self.zone_capturable = ZoneCapturable(x, y, rayon=5.0, temps_capture=5.0)

        # Vague boss (multiple de 10)
        if self.vague % 10 == 0:
            x, y = self.position_spawn(loin=True)
            self.boss = Boss(x, y, vague=self.vague)
            # Quelques ennemis normaux en plus pour le challenge
            nb_extra = self.vague // 5
            for _ in range(nb_extra):
                bx, by = self.position_spawn()
                self.ajouter_ennemi_nul(Ennemi_nul(bx, by, vitesse=1.6 + 0.04 * self.vague))
        else:
            total_ennemis = self.vague
            nb_tireurs = self.vague // 4
            nb_contact = total_ennemis - nb_tireurs

            for _ in range(nb_contact):
                x, y = self.position_spawn()
                self.ajouter_ennemi_nul(Ennemi_nul(x, y, vitesse=1.4 + 0.05 * self.vague))
            for _ in range(nb_tireurs):
                x, y = self.position_spawn()
                self.ajouter_ennemi(Ennemi(x, y, vitesse=0.9 + 0.03 * self.vague))

        self.attente_prochaine_vague = False
        self.temps_avant_prochaine_vague = 0.0

    def position_spawn(self, loin=False):
        """Spawn sur les bords de la map, loin du robot."""
        if self.robot is not None:
            cx, cy = self.robot.x, self.robot.y
        else:
            cx, cy = 0.0, 0.0

        marge_bord = 1.5
        # On essaie de spawner assez loin du robot
        dist_min = 8.0 if not loin else 14.0

        for _ in range(30):
            cote = random.choice(["haut", "bas", "gauche", "droite"])
            demi_l = self.largeur / 2
            demi_h = self.hauteur / 2

            if cote == "haut":
                x = random.uniform(-demi_l + marge_bord, demi_l - marge_bord)
                y = random.uniform(cy + dist_min, demi_h - marge_bord)
                y = min(y, demi_h - marge_bord)
            elif cote == "bas":
                x = random.uniform(-demi_l + marge_bord, demi_l - marge_bord)
                y = random.uniform(-demi_h + marge_bord, cy - dist_min)
                y = max(y, -demi_h + marge_bord)
            elif cote == "gauche":
                x = random.uniform(-demi_l + marge_bord, cx - dist_min)
                x = max(x, -demi_l + marge_bord)
                y = random.uniform(-demi_h + marge_bord, demi_h - marge_bord)
            else:
                x = random.uniform(cx + dist_min, demi_l - marge_bord)
                x = min(x, demi_l - marge_bord)
                y = random.uniform(-demi_h + marge_bord, demi_h - marge_bord)

            if math.hypot(x - cx, y - cy) >= dist_min:
                return x, y

        # Fallback
        angle = random.uniform(0, 2 * math.pi)
        r = dist_min + random.uniform(0, 3)
        return (
            max(-self.largeur / 2 + 1, min(self.largeur / 2 - 1, cx + math.cos(angle) * r)),
            max(-self.hauteur / 2 + 1, min(self.hauteur / 2 - 1, cy + math.sin(angle) * r))
        )

    # ------------------------------------------------------------------
    # Upgrades
    # ------------------------------------------------------------------

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

    def generer_choix_armes(self):
        from robot.armes import LaserGlace, LanceFlammes, Surf
        self.choix_armes = [
            (LaserGlace.NOM, LaserGlace.LABEL, LaserGlace.DESCRIPTION),
            (LanceFlammes.NOM, LanceFlammes.LABEL, LanceFlammes.DESCRIPTION),
            (Surf.NOM, Surf.LABEL, Surf.DESCRIPTION),
        ]

    def appliquer_choix_arme(self, index):
        if not self.en_pause_arme:
            return
        if index < 0 or index >= len(self.choix_armes):
            return
        nom, _, _ = self.choix_armes[index]
        
        # Permettre le changement d'arme même si le robot en a déjà une
        self.robot.appliquer_amelioration(nom)
        self.en_pause_arme = False
        self.choix_armes = []

    # ------------------------------------------------------------------
    # Boucle principale
    # ------------------------------------------------------------------

    def mettre_a_jour(self, dt, tirer_joueur=False, choix_upgrade=None):
        if self.robot is None or self.game_over:
            return

        if self.en_pause_arme:
            if choix_upgrade is not None:
                self.appliquer_choix_arme(choix_upgrade - 1)
            return

        if self.en_pause_upgrade:
            if choix_upgrade is not None:
                self.appliquer_choix_amelioration(choix_upgrade - 1)
            return

        old_x = self.robot.x
        old_y = self.robot.y
        old_orientation = self.robot.orientation

        self.robot.mettre_a_jour(dt)

        # Mettre à jour toutes les armes spéciales cumulées
        for arme in self.robot.armes_speciales:
            arme.mettre_a_jour(dt, self.robot, self)

        # Mettre à jour la zone capturable
        if self.zone_capturable and self.zone_capturable.actif:
            capture_reussie = self.zone_capturable.mettre_a_jour(dt, self.robot)
            if capture_reussie and self.robot_allie is None:
                # Créer le robot allié à la position de la zone
                self.robot_allie = RobotAllie(self.zone_capturable.x, self.zone_capturable.y)
                self.score += 100  # Bonus pour la capture

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
        if self.boss is not None and self.boss.actif:
            self.boss.mettre_a_jour(dt, self.robot, self)

        # Mettre à jour le robot allié
        if self.robot_allie and self.robot_allie.actif:
            self.robot_allie.mettre_a_jour(dt, self.robot, self)

        for projectile in self.projectiles:
            projectile.mettre_a_jour(dt)
        for item in self.items:
            item.mettre_a_jour(dt, self.robot)

        # Désactiver projectiles hors map
        marge = 2.0
        for projectile in self.projectiles:
            if (projectile.x < -demi_l - marge or projectile.x > demi_l + marge or
                    projectile.y < -demi_h - marge or projectile.y > demi_h + marge):
                projectile.actif = False

        self.gerer_collisions()

        self.ennemis = [e for e in self.ennemis if e.actif]
        self.ennemis_nuls = [e for e in self.ennemis_nuls if e.actif]
        self.projectiles = [p for p in self.projectiles if p.actif]
        self.items = [i for i in self.items if i.actif]
        if self.boss is not None and not self.boss.actif:
            self.boss = None

        if not self.robot.est_vivant():
            self.game_over = True
            return

        tout_mort = (
            len(self.ennemis) == 0
            and len(self.ennemis_nuls) == 0
            and self.boss is None
        )
        if tout_mort:
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
            x=x, y=y, vx=vx, vy=vy,
            rayon=self.robot.taille_projectile,
            owner="joueur",
            degats=self.robot.degats_projectile,
            duree_vie=3.5
        )
        self.ajouter_projectile(projectile)
        self.robot.tirer()

    def faire_tomber_xp(self, x, y, valeur=1):
        self.ajouter_item(ItemExperience(x, y, valeur=valeur))

    def faire_tomber_item_bonus(self, x, y):
        if random.random() < 0.10:
            if random.random() < 0.5:
                self.ajouter_item(ItemSoin(x, y))
            else:
                self.ajouter_item(ItemShield(x, y))

    def gerer_collisions(self):
        # Ennemis au contact
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

        # Boss au contact
        if self.boss is not None and self.boss.actif:
            if self.collision_cercles(
                self.robot.x, self.robot.y, self.robot.rayon,
                self.boss.x, self.boss.y, self.boss.rayon
            ):
                if self.boss.cooldown_contact <= 0:
                    self.robot.subir_degats(self.boss.degats_contact)
                    self.boss.cooldown_contact = 1.0

        # Projectiles
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

            elif projectile.owner == "joueur" or projectile.owner == "allie":
                # Boss
                if self.boss is not None and self.boss.actif:
                    if self.collision_cercles(
                        self.boss.x, self.boss.y, self.boss.rayon,
                        projectile.x, projectile.y, projectile.rayon
                    ):
                        self.boss.subir_degats(projectile.degats)
                        projectile.actif = False
                        if not self.boss.actif:
                            self.score += 500
                            # Beaucoup d'XP et d'items
                            for _ in range(8):
                                ox = self.boss.x + random.uniform(-1.5, 1.5)
                                oy = self.boss.y + random.uniform(-1.5, 1.5)
                                self.faire_tomber_xp(ox, oy, valeur=3)
                            self.ajouter_item(ItemSoin(self.boss.x, self.boss.y))
                        continue

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
                            self.faire_tomber_item_bonus(ennemi_nul.x, ennemi_nul.y)
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
                            self.faire_tomber_item_bonus(ennemi.x, ennemi.y)
                        break

        # Items
        for item in self.items:
            if not item.actif:
                continue
            if self.collision_cercles(
                self.robot.x, self.robot.y, self.robot.rayon,
                item.x, item.y, item.rayon
            ):
                item.actif = False
                if isinstance(item, ItemExperience):
                    montee = self.robot.ajouter_experience(item.valeur)
                    if montee:
                        self.en_pause_upgrade = True
                        self.generer_choix_ameliorations()
                        if self.robot.niveau_est_multiple_de_3():
                            self.en_pause_arme = True
                            self.generer_choix_armes()
                elif isinstance(item, ItemSoin):
                    self.robot.soigner(1)
                elif isinstance(item, ItemShield):
                    self.robot.activer_shield(duree=8.0)

    @staticmethod
    def collision_cercles(x1, y1, r1, x2, y2, r2):
        dx = x1 - x2
        dy = y1 - y2
        return (dx * dx + dy * dy) <= (r1 + r2) ** 2