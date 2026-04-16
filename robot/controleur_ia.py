import math
from robot.controleur import Controleur


class ControleurIA(Controleur):
    """
    Priorités de décision (ordre décroissant) :

    1. ESQUIVE PROJECTILE améliorée avec prédiction de trajectoire
    2. FUITE MASSE        - pression vectorielle ennemis trop forte
    3. ITEM               - item proche et zone sûre
    4. CIBLAGE            - attaque l'ennemi proche ou le boss
    """

    # Paramètres d'esquive optimisés pour meilleure réactivité
    RAYON_DANGER_PROJ_BASE   = 6.0   # rayon de détection augmenté
    TEMPS_REACTION_PROJ_BASE = 3.5   # fenêtre de réaction augmentée
    CONE_DANGER_PROJ_BASE    = 0.95   # cône de danger élargi
    SEUIL_ESQUIVE_BASE       = 0.10  # seuil plus sensible
    
    # Paramètres simplifiés
    FACTEUR_VITESSE_ROBOT = 0.25   # influence réduite pour plus de stabilité
    FACTEUR_DENSITE_PROJ  = 0.20  # ajustement plus modéré
    PREDICTION_STEPS      = 12     # moins de pas pour plus de rapidité

    def __init__(self, v_max=3.0, omega_max=3.5,
                 seuil_fuite=2.2, rayon_influence=4.0,
                 distance_attraction_item=4.0, seuil_danger_item=1.8):
        self.v_max = v_max
        self.omega_max = omega_max
        self.seuil_fuite = seuil_fuite
        self.rayon_influence = rayon_influence
        self.distance_attraction_item = distance_attraction_item
        self.seuil_danger_item = seuil_danger_item
        self.env = None
        
        # Paramètres adaptatifs calculés
        self.rayon_danger_proj = self.RAYON_DANGER_PROJ_BASE
        self.temps_reaction_proj = self.TEMPS_REACTION_PROJ_BASE
        self.cone_danger_proj = self.CONE_DANGER_PROJ_BASE
        self.seuil_esquive = self.SEUIL_ESQUIVE_BASE

        self.mode_esquive = False
        self.temps_esquive = 0.0
        self.duree_esquive_min = 0.25

        self.evade_x_mem = 0.0
        self.evade_y_mem = 0.0

    def set_environnement(self, env):
        self.env = env

    def lire_commande(self):
        if self.env is None or self.env.game_over:
            return self._commande_nulle()

        if getattr(self.env, "en_pause_upgrade", False) or getattr(self.env, "en_pause_arme", False):
            return self._commande_nulle()

        robot = self.env.robot
        boss = self.env.boss if (self.env.boss is not None and self.env.boss.actif) else None
        ennemi_proche = self._ennemi_le_plus_proche_tous()
        item_proche = self._item_le_plus_proche()

        dist_ennemi = (
            math.hypot(ennemi_proche.x - robot.x, ennemi_proche.y - robot.y)
            if ennemi_proche else float("inf")
        )
        dist_item = (
            math.hypot(item_proche.x - robot.x, item_proche.y - robot.y)
            if item_proche else float("inf")
        )

        cible_tir = self._choisir_cible_tir(boss, ennemi_proche)

        # ------------------------------------------------------------------
        # 1) VERROU D'ESQUIVE
        # ------------------------------------------------------------------
        if getattr(self, "temps_esquive", 0.0) > 0.0:
            self.temps_esquive -= 1.0 / 60.0
            if self.temps_esquive < 0.0:
                self.temps_esquive = 0.0

        if getattr(self, "temps_esquive", 0.0) > 0.0:
            return self._commande_esquive(
                robot,
                self.evade_x_mem,
                self.evade_y_mem,
                1.0,
                None
            )

        # ------------------------------------------------------------------
        # 2) NOUVELLE ESQUIVE
        # ------------------------------------------------------------------
        self._mettre_a_jour_parametres_adaptatifs(robot)
        evade_x, evade_y, force = self._vecteur_esquive_ameliore(robot)

        if force > self.seuil_esquive:
            self.evade_x_mem = evade_x
            self.evade_y_mem = evade_y
            self.temps_esquive = self.duree_esquive_min
            return self._commande_esquive(robot, evade_x, evade_y, force, None)

        # ------------------------------------------------------------------
        # 3) FIN DE MANCHE : ALLER CHERCHER LES ITEMS MÊME LOIN
        # ------------------------------------------------------------------
        plus_d_ennemis = (
            ennemi_proche is None
            and (boss is None)
        )

        if plus_d_ennemis and item_proche is not None:
            return self._commande_vers_item(robot, item_proche, None)

        # ------------------------------------------------------------------
        # 4) ZONE CAPTURABLE
        # ------------------------------------------------------------------
        if getattr(self.env, "zone_capturable", None) and self.env.zone_capturable.actif:
            zone = self.env.zone_capturable
            dist_zone = math.hypot(zone.x - robot.x, zone.y - robot.y)

            if dist_zone > zone.rayon + robot.rayon:
                return self._commande_vers_zone(robot, zone, cible_tir)

        # ------------------------------------------------------------------
        # 5) FUITE MASSE
        # ------------------------------------------------------------------
        fuite_x, fuite_y, pression = self._vecteur_fuite()
        if pression > 0.6:
            return self._commande_fuite(robot, fuite_x, fuite_y, cible_tir)

        # ------------------------------------------------------------------
        # 6) ITEM PROCHE SI ZONE ASSEZ SÛRE
        # ------------------------------------------------------------------
        if (
            item_proche is not None
            and dist_item < self.distance_attraction_item
            and dist_ennemi > self.seuil_danger_item
        ):
            return self._commande_vers_item(robot, item_proche, cible_tir)

        # ------------------------------------------------------------------
        # 7) ATTAQUE
        # ------------------------------------------------------------------
        if cible_tir is not None:
            dist_sec = 2.5 if cible_tir is boss else 0.5
            return self._commande_vers_cible(robot, cible_tir, dist_sec)

        return self._commande_nulle()

    def _mettre_a_jour_parametres_adaptatifs(self, robot):
        """Ajuste dynamiquement les paramètres d'esquive selon l'état du jeu."""
        nb_proj_ennemis = sum(1 for p in self.env.projectiles if p.actif and p.owner == "ennemi")
        
        # Ajustements plus simples et prévisibles
        facteur_densite = 1.0 + self.FACTEUR_DENSITE_PROJ * min(nb_proj_ennemis / 3.0, 1.0)
        
        vitesse_robot = math.hypot(getattr(robot, 'vx', 0), getattr(robot, 'vy', 0))
        facteur_vitesse = 1.0 + self.FACTEUR_VITESSE_ROBOT * (vitesse_robot / self.v_max)
        
        # Paramètres plus réactifs
        self.rayon_danger_proj = self.RAYON_DANGER_PROJ_BASE * facteur_densite
        self.temps_reaction_proj = self.TEMPS_REACTION_PROJ_BASE * facteur_vitesse
        self.cone_danger_proj = self.CONE_DANGER_PROJ_BASE * (1.0 + 0.05 * nb_proj_ennemis)
        self.seuil_esquive = self.SEUIL_ESQUIVE_BASE * (1.0 + 0.03 * nb_proj_ennemis)

    def _vecteur_esquive_ameliore(self, robot):
        """Version simplifiée et plus réactive."""
        ex, ey = 0.0, 0.0
        
        # Traitement direct des projectiles sans surcharge
        for proj in self.env.projectiles:
            if not proj.actif or proj.owner != "ennemi":
                continue
                
            menace = self._evaluer_menace_projectile(robot, proj)
            if menace is None:
                continue
                
            # Calcul immédiat de la direction d'esquive
            evade_dir = self._calculer_direction_esquive_optimale(robot, proj, menace)
            urgence = menace['urgence']
            
            ex += evade_dir[0] * urgence
            ey += evade_dir[1] * urgence
        
        magnitude = math.hypot(ex, ey)
        if magnitude > 1e-6:
            return ex / magnitude, ey / magnitude, magnitude
        return 0.0, 0.0, 0.0
    
    def _evaluer_menace_projectile(self, robot, proj):
        """Évalue la menace d'un projectile avec prédiction de trajectoire."""
        dx = robot.x - proj.x
        dy = robot.y - proj.y
        dist = math.hypot(dx, dy)
        
        if dist > self.rayon_danger_proj or dist < 1e-6:
            return None
            
        vit = math.hypot(proj.vx, proj.vy)
        if vit < 1e-6:
            return None
        
        position_predite = self._predire_collision(robot, proj)
        if position_predite is None:
            return None
            
        temps_collision, distance_collision = position_predite
        
        if temps_collision > self.temps_reaction_proj:
            return None
            
        urgence_base = 1.0 / max(0.05, temps_collision ** 2)
        facteur_proximite = 1.0 + (1.0 - min(distance_collision / 2.0, 1.0))
        
        angle_vers_robot = math.atan2(dy, dx)
        angle_proj = math.atan2(proj.vy, proj.vx)
        diff_angle = abs(self._normaliser_angle(angle_vers_robot - angle_proj))
        facteur_surprise = 1.5 if diff_angle < math.pi/4 else 1.0
        
        urgence = urgence_base * facteur_proximite * facteur_surprise
        
        return {
            'projectile': proj,
            'urgence': urgence,
            'temps_collision': temps_collision,
            'distance_collision': distance_collision,
            'angle_arrivee': math.atan2(proj.vy, proj.vx)
        }
    
    def _predire_collision(self, robot, proj):
        """Prédiction simplifiée et plus rapide."""
        dt = 0.06  # Pas plus grand pour plus de rapidité
        
        for i in range(self.PREDICTION_STEPS):
            t = i * dt
            
            # Position future du projectile
            proj_x = proj.x + proj.vx * t
            proj_y = proj.y + proj.vy * t
            
            # Position future estimée du robot
            robot_vx = getattr(robot, 'vx', 0)
            robot_vy = getattr(robot, 'vy', 0)
            robot_x = robot.x + robot_vx * t * 0.5  # Réduction de l'inertie
            robot_y = robot.y + robot_vy * t * 0.5
            
            dx = robot_x - proj_x
            dy = robot_y - proj_y
            dist_future = math.hypot(dx, dy)
            
            # Marge de sécurité augmentée
            if dist_future <= robot.rayon + proj.rayon + 0.2:
                return t, dist_future
                
        return None
    
    def _calculer_direction_esquive_optimale(self, robot, proj, menace):
        """Calcule la meilleure direction d'esquive pour un projectile donné."""
        dx = robot.x - proj.x
        dy = robot.y - proj.y
        
        vit = math.hypot(proj.vx, proj.vy)
        pnx = proj.vx / vit
        pny = proj.vy / vit
        
        cross = dx * pny - dy * pnx
        
        if cross >= 0:
            perp_x, perp_y = -pny, pnx
        else:
            perp_x, perp_y = pny, -pnx
        
        angle_arrivee = menace['angle_arrivee']
        angle_vers_robot = math.atan2(dy, dx)
        diff_angle = abs(self._normaliser_angle(angle_arrivee - angle_vers_robot))
        
        if diff_angle < math.pi/6:  # Projectile venant de face
            recul_x = -pnx * 0.3
            recul_y = -pny * 0.3
            evade_x = perp_x * 0.7 + recul_x
            evade_y = perp_y * 0.7 + recul_y
        else:
            evade_x, evade_y = perp_x, perp_y
        
        norm = math.hypot(evade_x, evade_y)
        if norm > 1e-6:
            evade_x /= norm
            evade_y /= norm
        
        evade_x, evade_y = self._ajuster_pour_bords(robot, evade_x, evade_y)
        
        return evade_x, evade_y

    def _ajuster_pour_bords(self, robot, px, py):
        """Ajuste la direction pour éviter les bords et les obstacles."""
        marge = 2.0
        demi_l = self.env.largeur / 2
        demi_h = self.env.hauteur / 2

        future_x = robot.x + px * 1.5
        future_y = robot.y + py * 1.5

        if future_x < -demi_l + marge or future_x > demi_l - marge:
            px = -px
        if future_y < -demi_h + marge or future_y > demi_h - marge:
            py = -py
        
        px, py = self._ajuster_pour_obstacles(robot, px, py)
        return px, py
    
    def _ajuster_pour_obstacles(self, robot, px, py):
        """Ajuste la direction d'esquive pour éviter les obstacles."""
        if not self.env.obstacles:
            return px, py
        
        test_distance = 1.5
        test_x = robot.x + px * test_distance
        test_y = robot.y + py * test_distance
        
        for obs in self.env.obstacles:
            if obs.collision(test_x, test_y, robot.rayon + 0.2):
                dx = test_x - obs.x
                dy = test_y - obs.y
                dist = math.hypot(dx, dy)
                
                if dist > 1e-6:
                    px = dx / dist
                    py = dy / dist
                else:
                    import random
                    angle = random.uniform(0, 2 * math.pi)
                    px = math.cos(angle)
                    py = math.sin(angle)
                break
        
        return px, py

    def _commande_esquive(self, robot, evade_x, evade_y, force, cible_tir):
        angle_esquive = math.atan2(evade_y, evade_x)
        diff = self._normaliser_angle(angle_esquive - robot.orientation)

        if abs(diff) > 0.08:
            omega = self.omega_max if diff > 0 else -self.omega_max
        else:
            omega = 0.0

        vitesse = min(self.v_max * 1.3, self.v_max * (1.0 + 0.3 * min(force, 1.5)))

        if abs(diff) < 0.20:
            v = vitesse
        elif abs(diff) < 0.50:
            v = vitesse * 0.25
        else:
            v = 0.0

        tirer = False
        return self._cmd(v, omega, tirer)

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

    def _choisir_cible_tir(self, boss, ennemi_proche):
        robot = self.env.robot
        if ennemi_proche is not None:
            dist = math.hypot(ennemi_proche.x - robot.x, ennemi_proche.y - robot.y)
            if dist < 3.5:
                return ennemi_proche
        if boss is not None:
            return boss
        return ennemi_proche

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

    def _commande_vers_zone(self, robot, zone, cible_tir):
        """Commande pour se diriger vers la zone capturable."""
        # Calculer l'angle vers la zone
        dx = zone.x - robot.x
        dy = zone.y - robot.y
        angle_vers_zone = math.atan2(dy, dx)
        
        # Calculer l'erreur d'angle
        angle_erreur = self._normaliser_angle(angle_vers_zone - robot.orientation)
        
        # Se déplacer vers la zone avec vitesse maximale
        v = self.v_max
        # Correction proportionnelle pour l'orientation
        omega = max(-self.omega_max, min(self.omega_max, 3.0 * angle_erreur))
        
        return self._cmd(v, omega, cible_tir is not None and robot.peut_tirer())

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
