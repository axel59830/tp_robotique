import pygame
from robot.robot_mobile import RobotMobile
from robot.moteur import MoteurDifferentiel
from robot.controleur import ControleurClavierPygame
from robot.vue_pygame import VuePygame
from robot.environnement import Environnement
from robot.obstacle import ObstacleCirculaire
from robot.ennemi import Ennemi
from robot.ennemi_nul import Ennemi_nul



robot = RobotMobile(moteur=MoteurDifferentiel())
env = Environnement()
env.ajouter_robot(robot)


# env.ajouter_obstacle(ObstacleCirculaire(2, 1, 0.5))
# env.ajouter_obstacle(ObstacleCirculaire(-1, -1, 0.7))
# env.ajouter_obstacle(ObstacleCirculaire(0, 3, 0.4))
# env.ajouter_obstacle(ObstacleCirculaire(-2, 2, 0.6))

controleur = ControleurClavierPygame()
vue = VuePygame()

dt = 0.02
running = True

ennemi = Ennemi(3, 3)
env.ajouter_ennemi(ennemi)
print(len(env.ennemis))

ennemi_nul = Ennemi_nul(5, -5)
env.ajouter_ennemi_nul(ennemi_nul)


while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    commande = controleur.lire_commande()
    robot.commander(**commande)

    env.mettre_a_jour(dt)

    vue.dessiner_environnement(env)
    vue.tick(60)
    

pygame.quit()