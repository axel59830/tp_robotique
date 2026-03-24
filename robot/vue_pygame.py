import pygame
import math
from robot.item import ItemExperience, ItemSoin, ItemShield


class VuePygame:

    def __init__(self, largeur=900, hauteur=700, scale=70):
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

    def convertir_coordonnees(self, x, y):
        px = int(self.largeur / 2 + x * self.scale)
        py = int(self.hauteur / 2 - y * self.scale)
        return px, py

    def dessiner_obstacle_circulaire(self, obstacle):
        x, y = self.convertir_coordonnees(obstacle.x, obstacle.y)
        r = int(obstacle.rayon * self.scale)
        pygame.draw.circle(self.screen, (120, 120, 120), (x, y), r)

    def dessiner_environnement(self, environnement):
        self.screen.fill((240, 240, 240))

        demi_l = environnement.largeur / 2
        demi_h = environnement.hauteur / 2
        x1, y1 = self.convertir_coordonnees(-demi_l, demi_h)
        x2, y2 = self.convertir_coordonnees(demi_l, -demi_h)
        rect = pygame.Rect(x1, y1, x2 - x1, y2 - y1)
        pygame.draw.rect(self.screen, (200, 200, 200), rect, 3)

        for obs in environnement.obstacles:
            obs.dessiner(self)

        robot = environnement.robot
        x, y = self.convertir_coordonnees(robot.x, robot.y)
        r = int(robot.rayon * self.scale)

        # Couleur robot : shield > clignotement dégâts > normal
        if robot.shield_actif:
            # Aura shield animée (pulse)
            aura_r = r + 8 + int(4 * math.sin(pygame.time.get_ticks() * 0.01))
            pygame.draw.circle(self.screen, (80, 180, 255), (x, y), aura_r)
            couleur_robot = (0, 200, 255)
        elif robot.cooldown_degats > 0 and int(robot.cooldown_degats * 10) % 2 == 0:
            couleur_robot = (100, 170, 255)
        else:
            couleur_robot = (0, 90, 255)

        pygame.draw.circle(self.screen, couleur_robot, (x, y), r)

        x_dir = x + int((r + 10) * math.cos(robot.orientation))
        y_dir = y - int((r + 10) * math.sin(robot.orientation))
        pygame.draw.line(self.screen, (255, 0, 0), (x, y), (x_dir, y_dir), 3)

        for ennemi in environnement.ennemis:
            ex, ey = self.convertir_coordonnees(ennemi.x, ennemi.y)
            er = int(ennemi.rayon * self.scale)
            pygame.draw.circle(self.screen, (255, 150, 0), (ex, ey), er)

        for ennemi_nul in environnement.ennemis_nuls:
            ex, ey = self.convertir_coordonnees(ennemi_nul.x, ennemi_nul.y)
            er = int(ennemi_nul.rayon * self.scale)
            pygame.draw.circle(self.screen, (220, 40, 40), (ex, ey), er)

        # Items
        for item in environnement.items:
            ix, iy = self.convertir_coordonnees(item.x, item.y)

            if isinstance(item, ItemExperience):
                ir = max(3, int(item.rayon * self.scale))
                pygame.draw.circle(self.screen, (0, 200, 120), (ix, iy), ir)

            elif isinstance(item, ItemSoin):
                ir = max(4, int(item.rayon * self.scale))
                pygame.draw.circle(self.screen, (255, 80, 80), (ix, iy), ir)
                # Croix blanche
                pygame.draw.line(self.screen, (255, 255, 255), (ix - ir + 3, iy), (ix + ir - 3, iy), 3)
                pygame.draw.line(self.screen, (255, 255, 255), (ix, iy - ir + 3), (ix, iy + ir - 3), 3)

            elif isinstance(item, ItemShield):
                ir = max(4, int(item.rayon * self.scale))
                pygame.draw.circle(self.screen, (80, 180, 255), (ix, iy), ir)
                # Petit bouclier (cercle intérieur)
                pygame.draw.circle(self.screen, (255, 255, 255), (ix, iy), max(2, ir - 4), 2)

        for projectile in environnement.projectiles:
            px, py = self.convertir_coordonnees(projectile.x, projectile.y)
            pr = max(2, int(projectile.rayon * self.scale))
            couleur = (20, 20, 20) if projectile.owner == "joueur" else (140, 0, 140)
            pygame.draw.circle(self.screen, couleur, (px, py), pr)

        self.dessiner_hud(environnement)

        if environnement.en_pause_upgrade:
            self.dessiner_menu_upgrade(environnement)

        pygame.display.flip()

    def dessiner_hud(self, environnement):
        robot = environnement.robot

        texte_vie = self.font.render(f"Vie : {robot.vie}/{robot.vie_max}", True, (20, 20, 20))
        texte_score = self.font.render(f"Score : {environnement.score}", True, (20, 20, 20))
        texte_vague = self.font.render(f"Vague : {environnement.vague}", True, (20, 20, 20))
        texte_niveau = self.font.render(f"Niveau : {robot.niveau}", True, (20, 20, 20))

        nb_restants = len(environnement.ennemis) + len(environnement.ennemis_nuls)
        texte_restants = self.font.render(f"Ennemis restants : {nb_restants}", True, (20, 20, 20))

        self.screen.blit(texte_vie, (15, 10))
        self.screen.blit(texte_score, (15, 40))
        self.screen.blit(texte_vague, (15, 70))
        self.screen.blit(texte_restants, (15, 100))
        self.screen.blit(texte_niveau, (15, 130))

        self.dessiner_barre_xp(robot)

        # Indicateur shield actif
        if robot.shield_actif:
            shield_texte = self.font.render(
                f"🛡 SHIELD  {robot.shield_duree:.1f}s", True, (0, 160, 255)
            )
            self.screen.blit(shield_texte, (15, 195))

        aide = self.small_font.render(
            "Flèches/ZQSD : bouger | Espace : tirer | Clic : upgrade | R : recommencer",
            True, (60, 60, 60)
        )
        self.screen.blit(aide, (15, self.hauteur - 35))

        if environnement.attente_prochaine_vague and not environnement.game_over and not environnement.en_pause_upgrade:
            message = f"Prochaine vague dans {max(0, environnement.temps_avant_prochaine_vague):.1f}s"
            texte = self.big_font.render(message, True, (50, 50, 50))
            rect = texte.get_rect(center=(self.largeur // 2, 40))
            self.screen.blit(texte, rect)

        if environnement.game_over:
            overlay = pygame.Surface((self.largeur, self.hauteur), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            self.screen.blit(overlay, (0, 0))

            texte1 = self.big_font.render("GAME OVER", True, (255, 255, 255))
            texte2 = self.font.render("Clique ou appuie sur R pour recommencer", True, (255, 255, 255))
            texte3 = self.font.render(f"Score final : {environnement.score}", True, (255, 255, 255))

            rect1 = texte1.get_rect(center=(self.largeur // 2, self.hauteur // 2 - 30))
            rect2 = texte2.get_rect(center=(self.largeur // 2, self.hauteur // 2 + 10))
            rect3 = texte3.get_rect(center=(self.largeur // 2, self.hauteur // 2 + 45))

            self.screen.blit(texte1, rect1)
            self.screen.blit(texte2, rect2)
            self.screen.blit(texte3, rect3)

    def dessiner_barre_xp(self, robot):
        x = 15
        y = 165
        largeur = 240
        hauteur = 20

        pygame.draw.rect(self.screen, (180, 180, 180), (x, y, largeur, hauteur), border_radius=6)

        ratio = 0
        if robot.experience_pour_niveau_suivant > 0:
            ratio = robot.experience / robot.experience_pour_niveau_suivant

        largeur_remplie = int(largeur * ratio)
        pygame.draw.rect(self.screen, (0, 200, 120), (x, y, largeur_remplie, hauteur), border_radius=6)
        pygame.draw.rect(self.screen, (40, 40, 40), (x, y, largeur, hauteur), 2, border_radius=6)

        texte = self.small_font.render(
            f"XP : {robot.experience}/{robot.experience_pour_niveau_suivant}",
            True, (20, 20, 20)
        )
        self.screen.blit(texte, (x + 8, y - 22))

    def dessiner_menu_upgrade(self, environnement):
        overlay = pygame.Surface((self.largeur, self.hauteur), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        boite_largeur = 560
        boite_hauteur = 320
        boite_x = (self.largeur - boite_largeur) // 2
        boite_y = (self.hauteur - boite_hauteur) // 2

        pygame.draw.rect(self.screen, (245, 245, 245),
                         (boite_x, boite_y, boite_largeur, boite_hauteur), border_radius=18)
        pygame.draw.rect(self.screen, (40, 40, 40),
                         (boite_x, boite_y, boite_largeur, boite_hauteur), 3, border_radius=18)

        titre = self.big_font.render("Choisis une amélioration", True, (20, 20, 20))
        self.screen.blit(titre, (boite_x + 90, boite_y + 25))

        mx, my = pygame.mouse.get_pos()

        for i, (_, label) in enumerate(environnement.choix_ameliorations):
            yy = boite_y + 95 + i * 65
            rect = pygame.Rect(boite_x + 40, yy, 480, 45)

            # Survol souris
            couleur_fond = (190, 220, 255) if rect.collidepoint(mx, my) else (220, 220, 220)
            pygame.draw.rect(self.screen, couleur_fond, rect, border_radius=10)

            texte = self.font.render(f"{i+1} - {label}", True, (20, 20, 20))
            self.screen.blit(texte, (boite_x + 60, yy + 10))

        aide = self.small_font.render("Clique sur un choix", True, (70, 70, 70))
        self.screen.blit(aide, (boite_x + 200, boite_y + 275))

    def tick(self, fps=60):
        return self.clock.tick(fps) / 1000.0