import math
import random
import pygame


class RobotAllie:
    """
    Robot allié qui tire automatiquement sur les ennemis.
    Apparaît après capture de la zone capturable.
    """
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rayon = 0.4
        self.orientation = 0.0
        self.vitesse = 0.0
        self.vitesse_max = 2.0
        
        # Caractéristiques de tir
        self.vitesse_projectile = 8.0
        self.taille_projectile = 0.08
        self.degats_projectile = 1
        self.cadence_tir = 0.8  # Temps entre chaque tir (secondes)
        self.cooldown_tir = 0.0
        self.portee_tir = 6.0  # Portée maximale de détection des ennemis
        
        # Positionnement par rapport au robot principal
        self.distance_au_robot = 2.0  # Distance à maintenir du robot principal
        self.angle_au_robot = 0.0  # Angle autour du robot principal
        
        # État
        self.actif = True
        
    def mettre_a_jour(self, dt, robot_principal, environnement):
        """Met à jour le robot allié."""
        if not self.actif:
            return
            
        # Mettre à jour le cooldown de tir
        if self.cooldown_tir > 0:
            self.cooldown_tir -= dt
            
        # Positionnement autour du robot principal
        self._se_positionner(dt, robot_principal)
        
        # Tir automatique sur les ennemis
        if self.cooldown_tir <= 0:
            self._tirer_si_ennemi_proche(environnement)
    
    def _se_positionner(self, dt, robot_principal):
        """Positionne le robot allié autour du robot principal."""
        # Calculer la position cible autour du robot principal
        cible_x = robot_principal.x + math.cos(self.angle_au_robot) * self.distance_au_robot
        cible_y = robot_principal.y + math.sin(self.angle_au_robot) * self.distance_au_robot
        
        # Mouvement doux vers la position cible
        dx = cible_x - self.x
        dy = cible_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0.1:
            # Se déplacer vers la position cible
            self.x += (dx / distance) * self.vitesse_max * dt
            self.y += (dy / distance) * self.vitesse_max * dt
            
            # Orienter vers la direction du mouvement
            self.orientation = math.atan2(dy, dx)
        else:
            # Tourner lentement autour du robot principal
            self.angle_au_robot += dt * 0.5  # Rotation lente
    
    def _tirer_si_ennemi_proche(self, environnement):
        """Tire automatiquement sur l'ennemi le plus proche dans la portée."""
        ennemi_cible = self._trouver_ennemi_plus_proche(environnement)
        
        if ennemi_cible:
            # Calculer l'angle vers l'ennemi
            dx = ennemi_cible.x - self.x
            dy = ennemi_cible.y - self.y
            self.orientation = math.atan2(dy, dx)
            
            # Tirer
            self._tirer(environnement)
            self.cooldown_tir = self.cadence_tir
    
    def _trouver_ennemi_plus_proche(self, environnement):
        """Trouve l'ennemi le plus proche dans la portée de tir."""
        ennemi_proche = None
        distance_min = self.portee_tir
        
        # Vérifier les ennemis normaux
        for ennemi in environnement.ennemis:
            if not ennemi.actif:
                continue
            distance = math.sqrt((ennemi.x - self.x)**2 + (ennemi.y - self.y)**2)
            if distance < distance_min:
                distance_min = distance
                ennemi_proche = ennemi
        
        # Vérifier les ennemis nuls
        for ennemi_nul in environnement.ennemis_nuls:
            if not ennemi_nul.actif:
                continue
            distance = math.sqrt((ennemi_nul.x - self.x)**2 + (ennemi_nul.y - self.y)**2)
            if distance < distance_min:
                distance_min = distance
                ennemi_proche = ennemi_nul
        
        # Vérifier le boss
        if environnement.boss and environnement.boss.actif:
            distance = math.sqrt((environnement.boss.x - self.x)**2 + (environnement.boss.y - self.y)**2)
            if distance < distance_min:
                distance_min = distance
                ennemi_proche = environnement.boss
        
        return ennemi_proche
    
    def _tirer(self, environnement):
        """Crée un projectile vers l'ennemi ciblé."""
        angle = self.orientation
        vitesse_proj = self.vitesse_projectile
        offset = self.rayon + 0.12
        x = self.x + math.cos(angle) * offset
        y = self.y + math.sin(angle) * offset
        vx = math.cos(angle) * vitesse_proj
        vy = math.sin(angle) * vitesse_proj
        
        # Importer Projectile localement pour éviter les imports circulaires
        from robot.projectile import Projectile
        projectile = Projectile(
            x=x, y=y, vx=vx, vy=vy,
            rayon=self.taille_projectile,
            owner="allie",
            degats=self.degats_projectile,
            duree_vie=2.5
        )
        environnement.ajouter_projectile(projectile)
    
        
    def dessiner(self, vue, cam_x, cam_y):
        """Dessine le robot allié."""
        if not self.actif:
            return
            
        # Convertir les coordonnées monde vers écran
        x_ecran, y_ecran = vue.monde_vers_ecran(self.x, self.y, cam_x, cam_y)
        rayon_ecran = int(self.rayon * vue.scale)
        
        # Dessiner l'image du robot allié si disponible
        if hasattr(vue, 'img_robot_allie') and vue.img_robot_allie:
            # Centrer l'image sur la position du robot allié
            img_rect = vue.img_robot_allie.get_rect(center=(x_ecran, y_ecran))
            vue.screen.blit(vue.img_robot_allie, img_rect)
        
        # Dessiner la direction
        longueur_direction = rayon_ecran + 8
        x_dir = x_ecran + int(longueur_direction * math.cos(self.orientation))
        y_dir = y_ecran - int(longueur_direction * math.sin(self.orientation))
        pygame.draw.line(vue.screen, (255, 255, 255), (x_ecran, y_ecran), (x_dir, y_dir), 2)
