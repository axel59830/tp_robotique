import math
import pygame


class ZoneCapturable:
    """
    Zone capturable qui apparaît à la vague 2.
    Le robot mobile doit rester dedans pendant 10 secondes pour recruter un allié.
    """
    
    def __init__(self, x, y, rayon=3.0, temps_capture=10.0):
        self.x = x
        self.y = y
        self.rayon = rayon
        self.temps_capture = temps_capture
        self.temps_dans_zone = 0.0
        self.capturée = False
        self.actif = True
        self.couleur = (100, 200, 255)  # Bleu clair
        self.couleur_progression = (50, 150, 200)  # Bleu plus foncé
        
    def mettre_a_jour(self, dt, robot):
        """Met à jour la zone et vérifie si le robot est dedans."""
        if not self.actif or self.capturée:
            return
            
        # Vérifier si le robot est dans la zone
        distance = math.sqrt((robot.x - self.x)**2 + (robot.y - self.y)**2)
        
        if distance <= self.rayon + robot.rayon:
            self.temps_dans_zone += dt
            if self.temps_dans_zone >= self.temps_capture:
                self.capturée = True
                self.actif = False
                return True  # Signal que la capture est réussie
        else:
            # Le robot est sorti de la zone, réinitialiser le temps
            self.temps_dans_zone = 0.0
            
        return False
    
    def dessiner(self, vue, cam_x, cam_y):
        """Dessine la zone capturable."""
        if not self.actif:
            return
            
        # Convertir les coordonnées monde vers écran
        x_ecran, y_ecran = vue.monde_vers_ecran(self.x, self.y, cam_x, cam_y)
        rayon_ecran = int(self.rayon * vue.scale)
        
        # Dessiner le cercle de la zone
        pygame.draw.circle(vue.screen, self.couleur, (x_ecran, y_ecran), rayon_ecran, 3)
        
        # Dessiner la progression (cercle intérieur)
        if self.temps_dans_zone > 0:
            progression = min(1.0, self.temps_dans_zone / self.temps_capture)
            rayon_progression = int(rayon_ecran * progression)
            
            # Créer une surface semi-transparente pour la progression
            surf = pygame.Surface((vue.largeur, vue.hauteur), pygame.SRCALPHA)
            alpha = int(100 * progression)
            pygame.draw.circle(surf, (*self.couleur_progression, alpha), (x_ecran, y_ecran), rayon_progression)
            vue.screen.blit(surf, (0, 0))
        
        # Dessiner le texte de progression
        if self.temps_dans_zone > 0:
            temps_restant = max(0, self.temps_capture - self.temps_dans_zone)
            texte = f"{temps_restant:.1f}s"
            font = pygame.font.SysFont("arial", 20)
            text_surface = font.render(texte, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(x_ecran, y_ecran))
            vue.screen.blit(text_surface, text_rect)
        else:
            # Texte d'indication
            texte = "CAPTURE ZONE"
            font = pygame.font.SysFont("arial", 16)
            text_surface = font.render(texte, True, (200, 200, 200))
            text_rect = text_surface.get_rect(center=(x_ecran, y_ecran))
            vue.screen.blit(text_surface, text_rect)
    
    def get_ratio_progression(self):
        """Retourne le ratio de progression (0.0 à 1.0)."""
        return min(1.0, self.temps_dans_zone / self.temps_capture)
