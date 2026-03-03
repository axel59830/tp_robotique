class Environnement:
    
    def __init__(self, largeur=10, hauteur=10):
        self.largeur = largeur
        self.hauteur = hauteur
        self.robot = None
        self.obstacles = []

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