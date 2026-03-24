import pygame
from robot.robot_mobile import RobotMobile
from robot.moteur import MoteurDifferentiel
from robot.controleur import ControleurClavierPygame
from robot.vue_pygame import VuePygame
from robot.environnement import Environnement


def main():
    robot = RobotMobile(moteur=MoteurDifferentiel())
    env = Environnement()
    env.ajouter_robot(robot)

    controleur = ControleurClavierPygame()
    vue = VuePygame()

    env.reinitialiser()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        commande = controleur.lire_commande()

        if commande["recommencer"] and env.game_over:
            env.reinitialiser()

        robot.commander(v=commande["v"], omega=commande["omega"])

        dt = vue.tick(60)
        env.mettre_a_jour(
            dt,
            tirer_joueur=commande["tirer"],
            choix_upgrade=commande["choix_upgrade"]
        )

        vue.dessiner_environnement(env)

    pygame.quit()


if __name__ == "__main__":
    main()