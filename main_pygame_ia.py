import pygame
from robot.robot_mobile import RobotMobile
from robot.moteur import MoteurDifferentiel
from robot.controleur_ia import ControleurIA
from robot.vue_pygame import VuePygame
from robot.environnement import Environnement


def main():
    robot = RobotMobile(moteur=MoteurDifferentiel())
    env = Environnement()
    env.ajouter_robot(robot)

    controleur = ControleurIA(
        v_max=3.4,
        omega_max=4.4,
        seuil_fuite=2.0,
        rayon_influence=4.2,
        distance_attraction_item=3.5,
    )
    controleur.set_environnement(env)

    vue = VuePygame()
    env.reinitialiser()

    running = True
    while running:
        choix_upgrade = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r and env.game_over:
                    env.reinitialiser()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                if env.en_pause_arme:
                    # Clic sur menu arme spéciale (2 choix)
                    for i, rect in enumerate(vue.get_arme_rects()):
                        if rect.collidepoint(mx, my):
                            choix_upgrade = i + 1
                            break

                elif env.en_pause_upgrade:
                    # Clic sur menu upgrade normal (3 choix)
                    for i, rect in enumerate(vue.get_upgrade_rects()):
                        if rect.collidepoint(mx, my):
                            choix_upgrade = i + 1
                            break

                elif env.game_over:
                    env.reinitialiser()

        commande = controleur.lire_commande()
        robot.commander(v=commande["v"], omega=commande["omega"])

        dt = vue.tick(60)
        env.mettre_a_jour(
            dt,
            tirer_joueur=commande["tirer"],
            choix_upgrade=choix_upgrade,
        )

        vue.dessiner_environnement(env)

    pygame.quit()


if __name__ == "__main__":
    main()