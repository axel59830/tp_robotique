from robot import ennemi, projectile, ennemi_nul


class Environnement:
    
    def __init__(self, largeur=10, hauteur=10):
        self.largeur = largeur
        self.hauteur = hauteur
        self.robot = None
        self.obstacles = []
        self.ennemis = []
        self.projectiles = []
        self.ennemis_nuls = []

    def ajouter_robot(self, robot):
        self.robot = robot

    def ajouter_obstacle(self, obstacle):
        self.obstacles.append(obstacle)

    def mettre_a_jour(self, dt, rayon_robot=0.3):

        if self.robot is None:
            return

        
        old_x = self.robot.x
        old_y = self.robot.y
        old_orientation = self.robot.orientation

        
        self.robot.mettre_a_jour(dt)

        
        for obs in self.obstacles:
            if obs.collision(self.robot.x, self.robot.y, rayon_robot):
                
                self.robot.x = old_x
                self.robot.y = old_y
                self.robot.orientation = old_orientation
                break

        for ennemi in self.ennemis:
            ennemi.mettre_a_jour(dt, self.robot, self)

        for ennemi_nul in self.ennemis_nuls:
            ennemi_nul.mettre_a_jour(dt, self.robot, self)

        # mise à jour projectiles
        for projectile in self.projectiles:
            projectile.mettre_a_jour(dt)

        # collision projectile → robot
        for projectile in self.projectiles:
            dx = projectile.x - self.robot.x
            dy = projectile.y - self.robot.y
            if (dx*dx + dy*dy) <= (projectile.rayon + 0.3)**2:
                print("Robot touché")
                projectile.actif = False

            # suppression projectiles inactifs
            self.projectiles = [p for p in self.projectiles if p.actif]
    
    def ajouter_ennemi(self, ennemi):
            self.ennemis.append(ennemi)

    def ajouter_ennemi_nul(self, ennemi_nul):
            self.ennemis_nuls.append(ennemi_nul)
    
    def ajouter_projectile(self, projectile):
            self.projectiles.append(projectile)