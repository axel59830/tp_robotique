import pygame
import math
from robot.item import ItemExperience, ItemSoin, ItemShield
from robot.armes import LaserGlace, LanceFlammes, Surf
from robot.boss import Boss


class VuePygame:

    def __init__(self, largeur=1000, hauteur=600, scale=55):
        pygame.init()
        self.screen = pygame.display.set_mode((largeur, hauteur))
        pygame.display.set_caption("Jeu de survie - Robot mobile")

        self.largeur = largeur
        self.hauteur = hauteur
        self.scale = scale
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("arial", 22)
        self.small_font = pygame.font.SysFont("arial", 18)
        self.big_font = pygame.font.SysFont("arial", 36, bold=True)
        self.huge_font = pygame.font.SysFont("arial", 52, bold=True)

        # Couleurs sol / grille style Vampire Survivors
        self.COULEUR_SOL = (28, 32, 22)
        self.COULEUR_GRILLE = (38, 44, 30)
        self.TAILLE_TUILE = 80  # pixels
        
        # Chargement des images
        self.img_robot = self._charger_image("img/robot_mobile.png", taille=(50, 50))
        self.img_robot_allie = self._charger_image("img/robot_allie.png", taille=(35, 35))
        self.img_ennemi_nul = self._charger_image("img/ennemi_nul.png", taille=(40, 40))
        self.img_ennemi = self._charger_image("img/ennemi.png", taille=(45, 45))
        self.img_boss = self._charger_image("img/boss.png", taille=(80, 80))

    # ------------------------------------------------------------------
    # Gestion des images
    # ------------------------------------------------------------------
    
    def _charger_image(self, chemin, taille=None):
        """Charge une image avec gestion d'erreur et redimensionnement optionnel."""
        try:
            image = pygame.image.load(chemin).convert_alpha()
            if taille:
                image = pygame.transform.scale(image, taille)
            return image
        except pygame.error as e:
            print(f"Erreur lors du chargement de l'image {chemin}: {e}")
            return None

    # ------------------------------------------------------------------
    # Conversion coordonnées
    # ------------------------------------------------------------------

    def monde_vers_ecran(self, x_monde, y_monde, cam_x, cam_y):
        """Convertit les coordonnées monde vers écran."""
        x_ecran = int((x_monde - cam_x) * self.scale + self.largeur / 2)
        y_ecran = int(-(y_monde - cam_y) * self.scale + self.hauteur / 2)
        return x_ecran, y_ecran

    # ------------------------------------------------------------------
    # Dessin sol et grille
    # ------------------------------------------------------------------

    def dessiner_sol(self, cam_x, cam_y, env):
        """Dessine le sol avec une grille."""
        self.screen.fill(self.COULEUR_SOL)
        taille_tuile_monde = self.TAILLE_TUILE / self.scale

        # Grille
        x_start = int(cam_x - self.largeur / (2 * self.scale))
        x_end = int(cam_x + self.largeur / (2 * self.scale))
        x = int(x_start / taille_tuile_monde) * taille_tuile_monde

        while x <= x_end:
            sx, _ = self.monde_vers_ecran(x, 0, cam_x, cam_y)
            if sx < 0:
                x += taille_tuile_monde
                continue
            if sx > self.largeur:
                break
            pygame.draw.line(self.screen, self.COULEUR_GRILLE, (sx, 0), (sx, self.hauteur), 1)
            x += taille_tuile_monde

        y = y_start = int(cam_y + self.hauteur / (2 * self.scale))
        y_end = int(cam_y - self.hauteur / (2 * self.scale))
        y = int(y_start / taille_tuile_monde) * taille_tuile_monde

        while y >= y_end:
            _, sy = self.monde_vers_ecran(0, y, cam_x, cam_y)
            if sy < 0:
                y -= taille_tuile_monde
                continue
            if sy > self.hauteur:
                break
            pygame.draw.line(self.screen, self.COULEUR_GRILLE, (0, sy), (self.largeur, sy), 1)
            y -= taille_tuile_monde

        # Bordures de la map
        demi_l = env.largeur / 2
        demi_h = env.hauteur / 2
        coins = [
            self.monde_vers_ecran(-demi_l, demi_h, cam_x, cam_y),
            self.monde_vers_ecran(demi_l, demi_h, cam_x, cam_y),
            self.monde_vers_ecran(demi_l, -demi_h, cam_x, cam_y),
            self.monde_vers_ecran(-demi_l, -demi_h, cam_x, cam_y),
        ]
        pygame.draw.polygon(self.screen, (60, 80, 50), coins, 4)

        # Zone hors map (assombrie)
        # On dessine 4 rectangles autour de la zone de jeu
        bx1, by1 = coins[0]
        bx2, by2 = coins[2]
        overlay = pygame.Surface((self.largeur, self.hauteur), pygame.SRCALPHA)
        # Haut
        if by1 > 0:
            pygame.draw.rect(overlay, (0, 0, 0, 120), (0, 0, self.largeur, by1))
        # Bas
        if by2 < self.hauteur:
            pygame.draw.rect(overlay, (0, 0, 0, 120), (0, by2, self.largeur, self.hauteur - by2))
        # Gauche
        if bx1 > 0:
            pygame.draw.rect(overlay, (0, 0, 0, 120), (0, 0, bx1, self.hauteur))
        # Droite
        if bx2 < self.largeur:
            pygame.draw.rect(overlay, (0, 0, 0, 120), (bx2, 0, self.largeur - bx2, self.hauteur))
        self.screen.blit(overlay, (0, 0))

    # ------------------------------------------------------------------
    # Dessin principal
    # ------------------------------------------------------------------

    def dessiner_environnement(self, environnement):
        robot = environnement.robot
        cam_x, cam_y = robot.x, robot.y

        self.dessiner_sol(cam_x, cam_y, environnement)

        for obs in environnement.obstacles:
            obs.dessiner(self)

        # Effets arme spéciale
        self.dessiner_effets_arme(robot, cam_x, cam_y)

        # Ennemis
        for ennemi in environnement.ennemis:
            ex, ey = self.monde_vers_ecran(ennemi.x, ennemi.y, cam_x, cam_y)
            er = max(4, int(ennemi.rayon * self.scale))
            
            # Dessiner l'image ennemi si disponible, sinon cercle de secours
            if self.img_ennemi:
                # Centrer l'image sur la position de l'ennemi
                img_rect = self.img_ennemi.get_rect(center=(ex, ey))
                self.screen.blit(self.img_ennemi, img_rect)
            else:
                # Cercle orange de secours si l'image ne charge pas
                pygame.draw.circle(self.screen, (255, 150, 0), (ex, ey), er)
            
            # Petite barre de vie
            self._dessiner_mini_vie(ex, ey, er, ennemi.vie, ennemi.vie)  # 2 pv max

        for ennemi_nul in environnement.ennemis_nuls:
            ex, ey = self.monde_vers_ecran(ennemi_nul.x, ennemi_nul.y, cam_x, cam_y)
            er = max(4, int(ennemi_nul.rayon * self.scale))
            
            # Dessiner l'image ennemi_nul si disponible, sinon cercle de secours
            if self.img_ennemi_nul:
                # Centrer l'image sur la position de l'ennemi
                img_rect = self.img_ennemi_nul.get_rect(center=(ex, ey))
                self.screen.blit(self.img_ennemi_nul, img_rect)
            else:
                # Cercle rouge de secours si l'image ne charge pas
                pygame.draw.circle(self.screen, (200, 40, 40), (ex, ey), er)

        # Boss
        if environnement.boss is not None and environnement.boss.actif:
            self.dessiner_boss(environnement.boss, cam_x, cam_y)

        # Items
        for item in environnement.items:
            ix, iy = self.monde_vers_ecran(item.x, item.y, cam_x, cam_y)
            if isinstance(item, ItemExperience):
                ir = max(3, int(item.rayon * self.scale))
                pygame.draw.circle(self.screen, (0, 220, 130), (ix, iy), ir)
            elif isinstance(item, ItemSoin):
                ir = max(5, int(item.rayon * self.scale))
                pygame.draw.circle(self.screen, (255, 80, 80), (ix, iy), ir)
                pygame.draw.line(self.screen, (255, 255, 255), (ix - ir + 3, iy), (ix + ir - 3, iy), 3)
                pygame.draw.line(self.screen, (255, 255, 255), (ix, iy - ir + 3), (ix, iy + ir - 3), 3)
            elif isinstance(item, ItemShield):
                ir = max(5, int(item.rayon * self.scale))
                pygame.draw.circle(self.screen, (80, 180, 255), (ix, iy), ir)
                pygame.draw.circle(self.screen, (255, 255, 255), (ix, iy), max(2, ir - 4), 2)

        # Projectiles
        for projectile in environnement.projectiles:
            px, py = self.monde_vers_ecran(projectile.x, projectile.y, cam_x, cam_y)
            pr = max(2, int(projectile.rayon * self.scale))
            couleur = (255, 240, 80) if projectile.owner == "joueur" else (200, 0, 200)
            pygame.draw.circle(self.screen, couleur, (px, py), pr)
            # Petit halo
            if projectile.owner == "joueur":
                pygame.draw.circle(self.screen, (255, 200, 0), (px, py), pr + 1, 1)

        # Robot
        rx, ry = self.monde_vers_ecran(robot.x, robot.y, cam_x, cam_y)
        r = int(robot.rayon * self.scale)

        # Dessiner l'ombre du robot
        pygame.draw.circle(self.screen, (20, 20, 60), (rx, ry), r + 3)

        # Dessiner l'image du robot si disponible, sinon cercle de secours
        if self.img_robot:
            # Centrer l'image sur la position du robot
            img_rect = self.img_robot.get_rect(center=(rx, ry))
            self.screen.blit(self.img_robot, img_rect)
        else:
            # Cercle bleu de secours si l'image ne charge pas
            if robot.shield_actif:
                couleur_robot = (0, 200, 255)
            elif robot.cooldown_degats > 0 and int(robot.cooldown_degats * 10) % 2 == 0:
                couleur_robot = (180, 80, 80)
            else:
                couleur_robot = (60, 140, 255)
            pygame.draw.circle(self.screen, couleur_robot, (rx, ry), r)

        # Dessiner l'aura du shield si actif
        if robot.shield_actif:
            aura_r = r + 10 + int(5 * math.sin(pygame.time.get_ticks() * 0.008))
            surf_aura = pygame.Surface((self.largeur, self.hauteur), pygame.SRCALPHA)
            pygame.draw.circle(surf_aura, (80, 180, 255, 80), (rx, ry), aura_r)
            pygame.draw.circle(surf_aura, (150, 220, 255, 180), (rx, ry), aura_r, 3)
            self.screen.blit(surf_aura, (0, 0))

        # Dessiner la direction du robot
        x_dir = rx + int((r + 10) * math.cos(robot.orientation))
        y_dir = ry - int((r + 10) * math.sin(robot.orientation))
        pygame.draw.line(self.screen, (255, 60, 60), (rx, ry), (x_dir, y_dir), 3)

        # Dessiner la zone capturable
        if environnement.zone_capturable and environnement.zone_capturable.actif:
            environnement.zone_capturable.dessiner(self, cam_x, cam_y)

        # Dessiner le robot allié
        if environnement.robot_allie and environnement.robot_allie.actif:
            environnement.robot_allie.dessiner(self, cam_x, cam_y)

        # HUD
        self.dessiner_hud(environnement)

        if environnement.en_pause_arme:
            self.dessiner_menu_arme(environnement)
        elif environnement.en_pause_upgrade:
            self.dessiner_menu_upgrade(environnement)

        pygame.display.flip()

    def dessiner_boss(self, boss, cam_x, cam_y):
        bx, by = self.monde_vers_ecran(boss.x, boss.y, cam_x, cam_y)
        br = int(boss.rayon * self.scale)

        # Aura rouge pulsante
        t = pygame.time.get_ticks()
        aura_r = br + 6 + int(5 * math.sin(t * 0.005))
        surf = pygame.Surface((self.largeur, self.hauteur), pygame.SRCALPHA)
        pygame.draw.circle(surf, (180, 0, 0, 60), (bx, by), aura_r)
        self.screen.blit(surf, (0, 0))

        # Dessiner l'image boss si disponible, sinon cercles de secours
        if self.img_boss:
            # Centrer l'image sur la position du boss
            img_rect = self.img_boss.get_rect(center=(bx, by))
            self.screen.blit(self.img_boss, img_rect)
        else:
            # Cercles violets de secours si l'image ne charge pas
            pygame.draw.circle(self.screen, (80, 0, 120), (bx, by), br)
            pygame.draw.circle(self.screen, (160, 0, 200), (bx, by), br, 4)

        # Barre de vie du boss (large, en bas de l'écran)
        self.dessiner_barre_vie_boss(boss)

        # Texte "BOSS" au-dessus
        t_boss = self.small_font.render("BOSS", True, (255, 80, 80))
        self.screen.blit(t_boss, (bx - t_boss.get_width() // 2, by - br - 22))

    def dessiner_barre_vie_boss(self, boss):
        """Barre de vie du boss compacte en bas au centre."""
        largeur_barre = 340
        hauteur_barre = 16
        x = (self.largeur - largeur_barre) // 2
        y = self.hauteur - 38

        pygame.draw.rect(self.screen, (40, 10, 10), (x, y, largeur_barre, hauteur_barre), border_radius=6)

        rempli = int(largeur_barre * boss.ratio_vie)
        if rempli > 0:
            g = int(50 + 100 * boss.ratio_vie)
            pygame.draw.rect(self.screen, (200, g, 0), (x, y, rempli, hauteur_barre), border_radius=6)

        pygame.draw.rect(self.screen, (160, 0, 0), (x, y, largeur_barre, hauteur_barre), 2, border_radius=6)

        label = self.small_font.render(f"Boss  {boss.vie}/{boss.vie_max}", True, (220, 220, 220))
        self.screen.blit(label, (x + largeur_barre // 2 - label.get_width() // 2, y - 20))

    def _dessiner_mini_vie(self, ex, ey, er, vie, vie_max):
        """Mini barre de vie sous un ennemi."""
        if vie >= vie_max:
            return
        bw = er * 2
        bh = 4
        bx = ex - er
        by = ey + er + 3
        pygame.draw.rect(self.screen, (80, 0, 0), (bx, by, bw, bh))
        rempli = int(bw * (vie / vie_max)) if vie_max > 0 else 0
        pygame.draw.rect(self.screen, (220, 60, 60), (bx, by, rempli, bh))

    def dessiner_effets_arme(self, robot, cam_x, cam_y):
        if not robot.armes_speciales:
            return
        rx, ry = self.monde_vers_ecran(robot.x, robot.y, cam_x, cam_y)
        
        # Dessiner les effets de toutes les armes cumulées
        for arme in robot.armes_speciales:
            if isinstance(arme, LaserGlace) and arme.en_flash:
                portee_px = int(20.0 * self.scale)
                angle = robot.orientation
                ex = rx + int(portee_px * math.cos(angle))
                ey = ry - int(portee_px * math.sin(angle))
                alpha = int(255 * (arme.flash_duree / arme.flash_max))
                surf = pygame.Surface((self.largeur, self.hauteur), pygame.SRCALPHA)
                pygame.draw.line(surf, (0, 255, 255, alpha), (rx, ry), (ex, ey), 8)
                pygame.draw.line(surf, (255, 255, 255, alpha), (rx, ry), (ex, ey), 2)
                self.screen.blit(surf, (0, 0))

            elif isinstance(arme, Surf) and arme.en_surf:
                # Dessiner le rectangle bleu du surf
                surf_x_px = int(arme.surf_x * self.scale)
                surf_y_px = int(arme.surf_y * self.scale)
                surf_w_px = int(arme.LARGEUR * self.scale)
                surf_h_px = int(arme.HAUTEUR * self.scale)
                
                # Convertir les coordonnées monde vers écran
                surf_screen_x, surf_screen_y = self.monde_vers_ecran(arme.surf_x, arme.surf_y, robot.x, robot.y)
                
                # Dessiner le rectangle bleu semi-transparent
                surf_rect = pygame.Surface((surf_w_px, surf_h_px), pygame.SRCALPHA)
                surf_rect.fill((0, 150, 255, 180))
                
                # Centrer le rectangle sur la position du surf
                rect_x = surf_screen_x - surf_w_px // 2
                rect_y = surf_screen_y - surf_h_px // 2
                self.screen.blit(surf_rect, (rect_x, rect_y))

            elif isinstance(arme, LanceFlammes) and arme.en_explosion:
                rayon_px = int(arme.RAYON_EXPLOSION * self.scale)
                alpha = int(180 * (arme.explosion_duree / arme.explosion_max))
                surf = pygame.Surface((self.largeur, self.hauteur), pygame.SRCALPHA)
                pygame.draw.circle(surf, (255, 120, 0, alpha), (rx, ry), rayon_px)
                pygame.draw.circle(surf, (255, 60, 0, min(255, alpha + 60)), (rx, ry), rayon_px, 5)
                self.screen.blit(surf, (0, 0))

    # ------------------------------------------------------------------
    # HUD
    # ------------------------------------------------------------------

    def dessiner_hud(self, environnement):
        robot = environnement.robot

        # Panneau HUD semi-transparent en haut à gauche
        hud = pygame.Surface((270, 230), pygame.SRCALPHA)
        hud.fill((0, 0, 0, 130))
        self.screen.blit(hud, (5, 5))

        def txt(texte, x, y, couleur=(220, 220, 220), font=None):
            f = font or self.font
            self.screen.blit(f.render(texte, True, couleur), (x, y))

        txt(f"Vie : {robot.vie} / {robot.vie_max}", 15, 12, (255, 100, 100))
        txt(f"Score : {environnement.score}", 15, 38, (220, 220, 100))
        txt(f"Vague : {environnement.vague}", 15, 64)
        nb = len(environnement.ennemis) + len(environnement.ennemis_nuls)
        if environnement.boss:
            nb += 1
        txt(f"Ennemis : {nb}", 15, 90)
        txt(f"Niveau : {robot.niveau}", 15, 116)

        self.dessiner_barre_xp(robot)

        y_hud = 200
        if robot.shield_actif:
            txt(f"SHIELD  {robot.shield_duree:.1f}s", 15, y_hud, (80, 180, 255))
            y_hud += 26

        # Afficher toutes les armes spéciales cumulées
        for arme in robot.armes_speciales:
            self.dessiner_barre_arme(arme, y_hud)
            y_hud += 26

        # Minimap
        self.dessiner_minimap(environnement)

        # Aide
        aide = self.small_font.render(
            "ZQSD/Flèches : bouger | Espace : tirer | Clic : upgrade",
            True, (120, 120, 120)
        )
        self.screen.blit(aide, (15, self.hauteur - 28))

        # Compte à rebours prochaine vague
        if (environnement.attente_prochaine_vague and not environnement.game_over
                and not environnement.en_pause_upgrade and not environnement.en_pause_arme):
            msg = f"Prochaine vague dans {max(0, environnement.temps_avant_prochaine_vague):.1f}s"
            t = self.big_font.render(msg, True, (240, 220, 80))
            shadow = self.big_font.render(msg, True, (40, 30, 0))
            cx = self.largeur // 2
            self.screen.blit(shadow, shadow.get_rect(center=(cx + 2, 42)))
            self.screen.blit(t, t.get_rect(center=(cx, 40)))

        if environnement.game_over:
            self._dessiner_game_over(environnement)

    def dessiner_minimap(self, environnement):
        """Minimap en bas à droite."""
        mm_w, mm_h = 160, 120
        mm_x = self.largeur - mm_w - 10
        mm_y = self.hauteur - mm_h - 10

        surf = pygame.Surface((mm_w, mm_h), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 150))
        pygame.draw.rect(surf, (80, 100, 60), (0, 0, mm_w, mm_h), 2)

        def vers_mm(wx, wy):
            nx = (wx + environnement.largeur / 2) / environnement.largeur
            ny = 1.0 - (wy + environnement.hauteur / 2) / environnement.hauteur
            return int(nx * mm_w), int(ny * mm_h)

        robot = environnement.robot
        for e in environnement.ennemis:
            ex, ey = vers_mm(e.x, e.y)
            pygame.draw.circle(surf, (255, 150, 0), (ex, ey), 2)
        for e in environnement.ennemis_nuls:
            ex, ey = vers_mm(e.x, e.y)
            pygame.draw.circle(surf, (200, 60, 60), (ex, ey), 2)
        if environnement.boss:
            bx, by = vers_mm(environnement.boss.x, environnement.boss.y)
            pygame.draw.circle(surf, (200, 0, 255), (bx, by), 5)
        for item in environnement.items:
            ix, iy = vers_mm(item.x, item.y)
            pygame.draw.circle(surf, (0, 220, 130), (ix, iy), 2)

        rx, ry = vers_mm(robot.x, robot.y)
        pygame.draw.circle(surf, (60, 140, 255), (rx, ry), 4)

        self.screen.blit(surf, (mm_x, mm_y))

    def dessiner_barre_xp(self, robot):
        x, y, w, h = 15, 168, 240, 18
        pygame.draw.rect(self.screen, (40, 40, 40), (x, y, w, h), border_radius=5)
        ratio = robot.experience / robot.experience_pour_niveau_suivant if robot.experience_pour_niveau_suivant > 0 else 0
        pygame.draw.rect(self.screen, (0, 200, 120), (x, y, int(w * ratio), h), border_radius=5)
        pygame.draw.rect(self.screen, (80, 80, 80), (x, y, w, h), 1, border_radius=5)
        t = self.small_font.render(f"XP {robot.experience}/{robot.experience_pour_niveau_suivant}", True, (200, 255, 200))
        self.screen.blit(t, (x + 6, y - 20))

    def dessiner_barre_arme(self, arme, y):
        x, w, h = 15, 240, 16
        if isinstance(arme, LaserGlace):
            couleur = (0, 220, 255)
            label = f"Laser glace  {max(0, arme.cooldown):.1f}s"
        elif isinstance(arme, Surf):
            couleur = (0, 150, 255)
            label = f"Surf  {max(0, arme.cooldown):.1f}s"
        else:
            couleur = (255, 120, 0)
            label = f"Lance-flammes  {max(0, arme.cooldown):.1f}s"
        pygame.draw.rect(self.screen, (40, 40, 40), (x, y, w, h), border_radius=5)
        pygame.draw.rect(self.screen, couleur, (x, y, int(w * arme.ratio_cooldown), h), border_radius=5)
        pygame.draw.rect(self.screen, (80, 80, 80), (x, y, w, h), 1, border_radius=5)
        t = self.small_font.render(label, True, couleur)
        self.screen.blit(t, (x + 4, y - 19))

    def _dessiner_game_over(self, environnement):
        overlay = pygame.Surface((self.largeur, self.hauteur), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        cx, cy = self.largeur // 2, self.hauteur // 2
        t1 = self.huge_font.render("GAME OVER", True, (255, 80, 80))
        t2 = self.font.render("Clique ou appuie sur R pour recommencer", True, (220, 220, 220))
        t3 = self.font.render(f"Score : {environnement.score}  |  Vague : {environnement.vague}", True, (220, 220, 100))
        self.screen.blit(t1, t1.get_rect(center=(cx, cy - 40)))
        self.screen.blit(t2, t2.get_rect(center=(cx, cy + 15)))
        self.screen.blit(t3, t3.get_rect(center=(cx, cy + 50)))

    def _dessiner_overlay(self):
        overlay = pygame.Surface((self.largeur, self.hauteur), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

    # ------------------------------------------------------------------
    # Menus upgrade / arme
    # ------------------------------------------------------------------

    def dessiner_menu_upgrade(self, environnement):
        self._dessiner_overlay()
        bx, by, bw, bh = self._boite_menu(320)
        self._dessiner_boite(bx, by, bw, bh)
        titre = self.big_font.render("Choisis une amélioration", True, (20, 20, 20))
        self.screen.blit(titre, (bx + 70, by + 25))
        mx, my = pygame.mouse.get_pos()
        for i, (_, label) in enumerate(environnement.choix_ameliorations):
            yy = by + 95 + i * 65
            rect = pygame.Rect(bx + 40, yy, 480, 45)
            couleur = (190, 220, 255) if rect.collidepoint(mx, my) else (220, 220, 220)
            pygame.draw.rect(self.screen, couleur, rect, border_radius=10)
            self.screen.blit(self.font.render(f"{i+1} - {label}", True, (20, 20, 20)), (bx + 60, yy + 10))
        self.screen.blit(self.small_font.render("Clique sur un choix", True, (70, 70, 70)),
                         (bx + 200, by + bh - 45))

    def dessiner_menu_arme(self, environnement):
        self._dessiner_overlay()
        bx, by, bw, bh = self._boite_menu(400)
        self._dessiner_boite(bx, by, bw, bh, couleur_bordure=(180, 120, 0))
        titre = self.big_font.render("★  Arme Spéciale  ★", True, (180, 120, 0))
        self.screen.blit(titre, titre.get_rect(centerx=bx + bw // 2, y=by + 20))
        sous = self.small_font.render(
            f"Niveau {environnement.robot.niveau} atteint !  Choisis ton arme :", True, (60, 60, 60))
        self.screen.blit(sous, sous.get_rect(centerx=bx + bw // 2, y=by + 65))
        mx, my = pygame.mouse.get_pos()
        for i, (nom, label, description) in enumerate(environnement.choix_armes):
            yy = by + 105 + i * 100
            rect = pygame.Rect(bx + 40, yy, 480, 80)
            
            # Vérifier si cette arme est déjà équipée (cumulée)
            arme_deja_equipee = any(arme.NOM == nom for arme in environnement.robot.armes_speciales)
            
            # Couleur différente si l'arme est déjà équipée
            if arme_deja_equipee:
                couleur = (150, 150, 150)  # Gris pour arme déjà équipée
                couleur_texte = (100, 100, 100)
            elif rect.collidepoint(mx, my):
                couleur = (255, 240, 180)  # Orange au survol
                couleur_texte = (120, 60, 0)
            else:
                couleur = (245, 230, 200)  # Beige normal
                couleur_texte = (120, 60, 0)
            
            pygame.draw.rect(self.screen, couleur, rect, border_radius=12)
            pygame.draw.rect(self.screen, (180, 120, 0), rect, 2, border_radius=12)
            
            # Texte de l'arme
            texte_arme = f"{i+1} - {label}"
            if arme_deja_equipee:
                texte_arme += " (ÉQUIPÉE)"
            
            self.screen.blit(self.font.render(texte_arme, True, couleur_texte), (bx + 60, yy + 10))
            self.screen.blit(self.small_font.render(description, True, (80, 60, 40)), (bx + 60, yy + 42))
        

    def _boite_menu(self, hauteur):
        bw, bh = 560, hauteur
        bx = (self.largeur - bw) // 2
        by = (self.hauteur - bh) // 2
        return bx, by, bw, bh

    def _dessiner_boite(self, bx, by, bw, bh, couleur_bordure=(40, 40, 40)):
        pygame.draw.rect(self.screen, (245, 245, 245), (bx, by, bw, bh), border_radius=18)
        pygame.draw.rect(self.screen, couleur_bordure, (bx, by, bw, bh), 3, border_radius=18)

    def get_upgrade_rects(self):
        _, by, _, _ = self._boite_menu(320)
        bx = (self.largeur - 560) // 2
        return [pygame.Rect(bx + 40, by + 95 + i * 65, 480, 45) for i in range(3)]

    def get_arme_rects(self):
        _, by, _, _ = self._boite_menu(360)
        bx = (self.largeur - 560) // 2
        return [pygame.Rect(bx + 40, by + 105 + i * 100, 480, 80) for i in range(3)]

    def dessiner_obstacle_circulaire(self, obstacle):
        pass  # à implémenter si besoin avec cam_x/cam_y

    def tick(self, fps=60):
        return self.clock.tick(fps) / 1000.0
