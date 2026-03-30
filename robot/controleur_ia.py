import math
from robot.controleur import Controleur


class ControleurIA(Controleur):
    """
    Priorités de décision (ordre décroissant) :

    1. ESQUIVE PROJECTILE — calcule un vecteur de répulsion cumulé de TOUS les
                            projectiles dangereux → déplacement diagonal fluide
    2. FUITE MASSE        — pression vectorielle ennemis trop forte → recul
    3. ITEM               — item proche et zone sûre → avance vers lui
    4. CIBLAGE            — attaque l'ennemi proche ou le boss
    """

    # ── Paramètres d'esquive ────────────────────────────────────────────
    RAYON_DANGER_PROJ   = 3.5   # rayon de détection (unités monde)
    TEMPS_REACTION_PROJ = 1.4   # fenêtre de réaction (secondes)
    CONE_DANGER_PROJ    = 0.55  # demi-angle du cône de danger (radians, ~31°)
    SEUIL_ESQUIVE       = 0.25  # magnitude min du vecteur cumulé pour déclencher

    def __init__(self, v_max=3.0, omega_max=3.5,
                 seuil_fuite=2.2,
                 rayon_influence=4.0,
                 distance_attraction_item=4.0,
                 seuil_danger_item=1.8):
        self.v_max = v_max
        self.omega_max = omega_max
        self.seuil_fuite = seuil_fuite
        self.rayon_influence = rayon_influence
        self.distance_attraction_item = distance_attraction_item
        self.seuil_danger_item = seuil_danger_item
        self.env = None

    def set_environnement(self, env):
        self.env = env

    # ------------------------------------------------------------------
    # Interface obligatoire
    # ------------------------------------------------------------------

    def lire_commande(self):
        if self.env is None or self.env.game_over:
            return self._commande_nulle()
        if getattr(self.env, 'en_pause_upgrade', False) or getattr(self.env, 'en_pause_arme', False):
            return self._commande_nulle()

        robot = self.env.robot
        boss = self.env.boss if (self.env.boss is not None and self.env.boss.actif) else None
        ennemi_proche = self._ennemi_le_plus_proche_tous()
        item_proche   = self._item_le_plus_proche()

        dist_ennemi = (
            math.hypot(ennemi_proche.x - robot.x, ennemi_proche.y - robot.y)
            if ennemi_proche else float("inf")
        )
        dist_item = (
            math.hypot(item_proche.x - robot.x, item_proche.y - robot.y)
            if item_proche else float("inf")
        )

        cible_tir = self._choisir_cible_tir(boss, ennemi_proche)

        # ── CAS 1 : ESQUIVE ─────────────────────────────────────────────
        evade_x, evade_y, force = self._vecteur_esquive(robot)
        if force > self.SEUIL_ESQUIVE:
            return self._commande_esquive(robot, evade_x, evade_y, force, cible_tir)

        # ── CAS 2 : FUITE MASSE ─────────────────────────────────────────
        fuite_x, fuite_y, pression = self._vecteur_fuite()
        if pression > 0.6:
            return self._commande_fuite(robot, fuite_x, fuite_y, cible_tir)

        # ── CAS 3 : ITEM ────────────────────────────────────────────────
        if (item_proche is not None
                and dist_item < self.distance_attraction_item
                and dist_ennemi > self.seuil_danger_item):
            return self._commande_vers_item(robot, item_proche, cible_tir)

        # ── CAS 4 : ATTAQUE ─────────────────────────────────────────────
        if cible_tir is not None:
            dist_sec = 2.5 if cible_tir is boss else 0.5
            return self._commande_vers_cible(robot, cible_tir, dist_sec)

        return self._commande_nulle()

    # ------------------------------------------------------------------
    # Choix cible tir
    # ------------------------------------------------------------------

    def _choisir_cible_tir(self, boss, ennemi_proche):
        robot = self.env.robot
        if ennemi_proche is not None:
            dist = math.hypot(ennemi_proche.x - robot.x, ennemi_proche.y - robot.y)
            if dist < 3.5:
                return ennemi_proche
        if boss is not None:
            return boss
        return ennemi_proche

    # ------------------------------------------------------------------
    # Esquive vectorielle (cumulée sur TOUS les projectiles dangereux)
    # ------------------------------------------------------------------

    def _vecteur_esquive(self, robot):
        """
        Pour chaque projectile ennemi dans le rayon et le cône de danger,
        calcule un vecteur de répulsion perpendiculaire à sa trajectoire,
        pondéré par l'urgence (1 / temps_impact²).

        Retourne (ex, ey normalisés, magnitude brute).
        """
        ex, ey = 0.0, 0.0

        for proj in self.env.projectiles:
            if not proj.actif or proj.owner != "ennemi":
                continue

            # Vecteur projectile → robot
            dx = robot.x - proj.x
            dy = robot.y - proj.y
            dist = math.hypot(dx, dy)

            if dist > self.RAYON_DANGER_PROJ or dist < 1e-6:
                continue

            vit = math.hypot(proj.vx, proj.vy)
            if vit < 1e-6:
                continue

            # Direction normalisée du projectile
            pnx = proj.vx / vit
            pny = proj.vy / vit

            # Le projectile converge-t-il vers le robot ?
            dot = dx * pnx + dy * pny   # > 0 si le proj se rapproche
            if dot <= 0:
                continue

            # Angle entre la direction du proj et la direction proj→robot
            # Si l'angle est grand, le proj passe loin
            cross = dx * pny - dy * pnx          # distance perpendiculaire signée
            perp_dist = abs(cross)
            rayon_col = robot.rayon + proj.rayon

            # Cône de danger : perp_dist / dist = sin(angle)
            if perp_dist > dist * math.sin(self.CONE_DANGER_PROJ) + rayon_col:
                continue

            temps_impact = dot / vit   # approximation
            if temps_impact > self.TEMPS_REACTION_PROJ:
                continue

            # Urgence : plus le projectile est proche et rapide, plus le poids est fort
            urgence = 1.0 / max(0.05, temps_impact ** 2)

            # Perpendiculaire dans le bon sens (s'éloigner de la trajectoire)
            # cross > 0 → robot est "à gauche" du proj → esquiver à gauche (-pny, pnx)
            # cross < 0 → robot est "à droite" du proj → esquiver à droite (pny, -pnx)
            if cross >= 0:
                perp_x, perp_y = -pny,  pnx
            else:
                perp_x, perp_y =  pny, -pnx

            # Bonus : si on s'éloigne aussi du bord, on ne change pas de côté
            perp_x, perp_y = self._ajuster_pour_bords(robot, perp_x, perp_y)

            ex += perp_x * urgence
            ey += perp_y * urgence

        magnitude = math.hypot(ex, ey)
        if magnitude > 1e-6:
            return ex / magnitude, ey / magnitude, magnitude
        return 0.0, 0.0, 0.0

    def _ajuster_pour_bords(self, robot, px, py):
        """
        Si le vecteur d'esquive pousse vers un bord, on l'inverse.
        """
        marge = 2.0
        demi_l = self.env.largeur / 2
        demi_h = self.env.hauteur / 2

        future_x = robot.x + px * 1.5
        future_y = robot.y + py * 1.5

        if future_x < -demi_l + marge or future_x > demi_l - marge:
            px = -px
        if future_y < -demi_h + marge or future_y > demi_h - marge:
            py = -py

        return px, py

    def _commande_esquive(self, robot, evade_x, evade_y, force, cible_tir):
        """
        Déplacement dans la direction d'esquive cumulée.
        L'orientation reste vers la cible de tir pour continuer à tirer.
        La vitesse est proportionnelle à l'urgence (plafonnée à v_max).
        """
        # Orientation toujours vers la cible
        omega, tirer = self._orienter_vers(robot, cible_tir)

        # Direction d'esquive souhaitée
        angle_esquive = math.atan2(evade_y, evade_x)
        diff = self._normaliser_angle(angle_esquive - robot.orientation)

        # Vitesse : avance ou recule selon si la direction est devant/derrière
        vitesse = min(self.v_max * 1.2, self.v_max * (1.0 + force * 0.3))  # léger boost d'urgence
        if abs(diff) < math.pi / 2:
            v = vitesse
        else:
            v = -vitesse

        return self._cmd(v, omega, tirer)

    # ------------------------------------------------------------------
    # Autres comportements
    # ------------------------------------------------------------------

    def _commande_fuite(self, robot, fuite_x, fuite_y, cible_tir):
        omega, tirer = self._orienter_vers(robot, cible_tir)
        angle_fuite = math.atan2(fuite_y, fuite_x)
        diff = abs(self._normaliser_angle(angle_fuite - robot.orientation))
        v = self.v_max if diff < math.pi / 2 else -self.v_max
        return self._cmd(v, omega, tirer)

    def _commande_vers_item(self, robot, item, cible_tir):
        dx = item.x - robot.x
        dy = item.y - robot.y
        dist = math.hypot(dx, dy)
        diff = self._normaliser_angle(math.atan2(dy, dx) - robot.orientation)
        omega = math.copysign(self.omega_max, diff) if abs(diff) > 0.05 else 0.0
        v = self.v_max if (dist > 0.25 and abs(diff) < math.pi / 2) else 0.0
        tirer = False
        if cible_tir is not None:
            dxe = cible_tir.x - robot.x
            dye = cible_tir.y - robot.y
            diff_e = abs(self._normaliser_angle(math.atan2(dye, dxe) - robot.orientation))
            tirer = diff_e < 0.35
        return self._cmd(v, omega, tirer)

    def _commande_vers_cible(self, robot, cible, dist_securite=0.5):
        omega, tirer = self._orienter_vers(robot, cible)
        dist = math.hypot(cible.x - robot.x, cible.y - robot.y)
        v = self.v_max if dist > dist_securite else 0.0
        return self._cmd(v, omega, tirer)

    # ------------------------------------------------------------------
    # Fuite vectorielle (masse ennemie)
    # ------------------------------------------------------------------

    def _vecteur_fuite(self):
        robot = self.env.robot
        fx, fy = 0.0, 0.0
        tous = (
            [e for e in self.env.ennemis if e.actif] +
            [e for e in self.env.ennemis_nuls if e.actif]
        )
        if self.env.boss and self.env.boss.actif:
            tous.append(self.env.boss)

        for ennemi in tous:
            dx = robot.x - ennemi.x
            dy = robot.y - ennemi.y
            dist = math.hypot(dx, dy)
            if dist < 1e-6 or dist > self.rayon_influence:
                continue
            poids = 1.0 / (dist * dist)
            fx += (dx / dist) * poids
            fy += (dy / dist) * poids

        mag = math.hypot(fx, fy)
        if mag > 1e-6:
            fx /= mag
            fy /= mag
            pression = min(1.0, mag / (1.0 / (self.seuil_fuite ** 2)))
        else:
            pression = 0.0
        return fx, fy, pression

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _orienter_vers(self, robot, cible):
        if cible is None:
            return 0.0, False
        dx = cible.x - robot.x
        dy = cible.y - robot.y
        angle = math.atan2(dy, dx)
        diff = self._normaliser_angle(angle - robot.orientation)
        omega = math.copysign(self.omega_max, diff) if abs(diff) > 0.05 else 0.0
        tirer = abs(diff) < 0.35
        return omega, tirer

    def _ennemi_le_plus_proche_tous(self):
        robot = self.env.robot
        tous = (
            [e for e in self.env.ennemis if e.actif] +
            [e for e in self.env.ennemis_nuls if e.actif]
        )
        if not tous:
            return None
        return min(tous, key=lambda e: math.hypot(e.x - robot.x, e.y - robot.y))

    def _item_le_plus_proche(self):
        robot = self.env.robot
        items = [i for i in self.env.items if i.actif]
        if not items:
            return None
        return min(items, key=lambda i: math.hypot(i.x - robot.x, i.y - robot.y))

    @staticmethod
    def _normaliser_angle(a):
        while a > math.pi:
            a -= 2 * math.pi
        while a < -math.pi:
            a += 2 * math.pi
        return a

    @staticmethod
    def _cmd(v, omega, tirer):
        return {"v": v, "omega": omega, "tirer": tirer,
                "recommencer": False, "choix_upgrade": None}

    @staticmethod
    def _commande_nulle():
        return {"v": 0.0, "omega": 0.0, "tirer": False,
                "recommencer": False, "choix_upgrade": None}
    