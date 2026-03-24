import math
from robot.controleur import Controleur


class ControleurIA(Controleur):
    """
    Contrôleur autonome pour RobotMobile.

    Principe clé :
    - Le robot s'oriente TOUJOURS vers l'ennemi le plus proche pour tirer en continu
    - Quand la pression ennemie est forte, il RECULE (v < 0) tout en restant face aux ennemis
    - Sinon il avance vers la cible (ennemi ou item XP)
    - Les upgrades sont laissées au joueur
    """

    def __init__(self, v_max=3.0, omega_max=3.5,
                 seuil_fuite=2.2,
                 rayon_influence=4.0,
                 distance_attraction_item=3.5):
        self.v_max = v_max
        self.omega_max = omega_max
        self.seuil_fuite = seuil_fuite
        self.rayon_influence = rayon_influence
        self.distance_attraction_item = distance_attraction_item
        self.env = None

    def set_environnement(self, env):
        self.env = env

    # ------------------------------------------------------------------
    # Interface obligatoire
    # ------------------------------------------------------------------

    def lire_commande(self):
        if self.env is None or self.env.game_over:
            return self._commande_nulle()

        if self.env.en_pause_upgrade:
            return self._commande_nulle()

        robot = self.env.robot
        cible_tir = self._ennemi_le_plus_proche_tous()

        # --- Orientation : toujours vers l'ennemi le plus proche ---
        if cible_tir is not None:
            dx_tir = cible_tir.x - robot.x
            dy_tir = cible_tir.y - robot.y
            angle_cible = math.atan2(dy_tir, dx_tir)
            diff_angle = self._normaliser_angle(angle_cible - robot.orientation)
            omega = math.copysign(self.omega_max, diff_angle) if abs(diff_angle) > 0.05 else 0.0
            tirer = abs(diff_angle) < 0.35
        else:
            # Pas d'ennemi : on tourne doucement
            omega = self.omega_max * 0.3
            tirer = False

        # --- Déplacement : fuite arrière ou approche ---
        fuite_x, fuite_y, pression = self._vecteur_fuite()

        if pression > 0.6:
            # Fuite : le robot est orienté vers les ennemis, donc reculer = v négatif
            # On vérifie que la direction de fuite est bien derrière le robot
            angle_fuite = math.atan2(fuite_y, fuite_x)
            diff_fuite = abs(self._normaliser_angle(angle_fuite - robot.orientation))

            if diff_fuite < math.pi / 2:
                # La fuite est devant → avancer (cas rare, ennemis derrière)
                v = self.v_max
            else:
                # La fuite est derrière → reculer (cas normal : ennemis devant)
                v = -self.v_max
        else:
            # Approche vers la cible
            cible_pos = self._choisir_cible_deplacement()
            if cible_pos is None:
                v = 0.0
            else:
                dx = cible_pos[0] - robot.x
                dy = cible_pos[1] - robot.y
                dist = math.hypot(dx, dy)

                if dist < 0.4:
                    v = 0.0
                else:
                    # Angle entre orientation du robot et direction de la cible
                    angle_vers_cible = math.atan2(dy, dx)
                    diff_vers_cible = self._normaliser_angle(angle_vers_cible - robot.orientation)

                    if abs(diff_vers_cible) < math.pi / 2:
                        v = self.v_max      # cible devant → avancer
                    else:
                        v = -self.v_max     # cible derrière → reculer vers elle

        return {
            "v": v,
            "omega": omega,
            "tirer": tirer,
            "recommencer": False,
            "choix_upgrade": None,
        }

    # ------------------------------------------------------------------
    # Fuite vectorielle
    # ------------------------------------------------------------------

    def _vecteur_fuite(self):
        """
        Vecteur de répulsion global pondéré par 1/dist².
        Retourne (fx, fy normalisés, pression).
        """
        robot = self.env.robot
        fx, fy = 0.0, 0.0

        tous_ennemis = (
            [e for e in self.env.ennemis if e.actif] +
            [e for e in self.env.ennemis_nuls if e.actif]
        )

        for ennemi in tous_ennemis:
            dx = robot.x - ennemi.x
            dy = robot.y - ennemi.y
            dist = math.hypot(dx, dy)

            if dist < 1e-6 or dist > self.rayon_influence:
                continue

            poids = 1.0 / (dist * dist)
            fx += (dx / dist) * poids
            fy += (dy / dist) * poids

        magnitude = math.hypot(fx, fy)
        if magnitude > 1e-6:
            fx /= magnitude
            fy /= magnitude
            pression = min(1.0, magnitude / (1.0 / (self.seuil_fuite ** 2)))
        else:
            pression = 0.0

        return fx, fy, pression

    # ------------------------------------------------------------------
    # Helpers cibles
    # ------------------------------------------------------------------

    def _choisir_cible_deplacement(self):
        robot = self.env.robot

        item = self._item_le_plus_proche()
        if item is not None:
            if math.hypot(item.x - robot.x, item.y - robot.y) < self.distance_attraction_item:
                return item.x, item.y

        ennemi_nul = self._ennemi_nul_le_plus_proche()
        if ennemi_nul is not None:
            return ennemi_nul.x, ennemi_nul.y

        ennemi = self._ennemi_le_plus_proche()
        if ennemi is not None:
            return ennemi.x, ennemi.y

        return None

    def _ennemi_le_plus_proche_tous(self):
        robot = self.env.robot
        tous = (
            [e for e in self.env.ennemis if e.actif] +
            [e for e in self.env.ennemis_nuls if e.actif]
        )
        if not tous:
            return None
        return min(tous, key=lambda e: math.hypot(e.x - robot.x, e.y - robot.y))

    def _ennemi_le_plus_proche(self):
        robot = self.env.robot
        ennemis = [e for e in self.env.ennemis if e.actif]
        if not ennemis:
            return None
        return min(ennemis, key=lambda e: math.hypot(e.x - robot.x, e.y - robot.y))

    def _ennemi_nul_le_plus_proche(self):
        robot = self.env.robot
        ennemis = [e for e in self.env.ennemis_nuls if e.actif]
        if not ennemis:
            return None
        return min(ennemis, key=lambda e: math.hypot(e.x - robot.x, e.y - robot.y))

    def _item_le_plus_proche(self):
        robot = self.env.robot
        items = [i for i in self.env.items if i.actif]
        if not items:
            return None
        return min(items, key=lambda i: math.hypot(i.x - robot.x, i.y - robot.y))

    # ------------------------------------------------------------------
    # Utilitaires
    # ------------------------------------------------------------------

    @staticmethod
    def _normaliser_angle(a):
        while a > math.pi:
            a -= 2 * math.pi
        while a < -math.pi:
            a += 2 * math.pi
        return a

    @staticmethod
    def _commande_nulle():
        return {
            "v": 0.0,
            "omega": 0.0,
            "tirer": False,
            "recommencer": False,
            "choix_upgrade": None,
        }