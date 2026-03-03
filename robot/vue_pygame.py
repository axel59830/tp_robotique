import pygame
import math


class VuePygame:

    def __init__(self, largeur=800, hauteur=600, scale=50):
        pygame.init()
        self.screen = pygame.display.set_mode((largeur, hauteur))
        pygame.display.set_caption("Simulation Robot Mobile")

        self.largeur = largeur
        self.hauteur = hauteur
        self.scale = scale
        self.clock = pygame.time.Clock()

    def convertir_coordonnees(self, x, y):
        px = int(self.largeur / 2 + x * self.scale)
        py = int(self.hauteur / 2 - y * self.scale)
        return px, py

    def dessiner_obstacle_circulaire(self, obstacle):
        x, y = self.convertir_coordonnees(obstacle.x, obstacle.y)
        r = int(obstacle.rayon * self.scale)
        pygame.draw.circle(self.screen, (255, 100, 100), (x, y), r)

    def dessiner_environnement(self, environnement):
        self.screen.fill((240, 240, 240))

        for obs in environnement.obstacles:
            obs.dessiner(self)

        robot = environnement.robot
        x, y = self.convertir_coordonnees(robot.x, robot.y)
        r = int(0.3 * self.scale)

        pygame.draw.circle(self.screen, (0, 0, 255), (x, y), r)

        x_dir = x + int(r * math.cos(robot.orientation))
        y_dir = y - int(r * math.sin(robot.orientation))

        pygame.draw.line(self.screen, (255, 0, 0), (x, y), (x_dir, y_dir), 3)

        pygame.display.flip()

    def tick(self, fps=60):
        self.clock.tick(fps)