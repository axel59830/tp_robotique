import pygame
from robot.robot_mobile import RobotMobile
from robot.moteur import MoteurDifferentiel
from robot.controleur_ia import ControleurIA
from robot.vue_pygame import VuePygame
from robot.environnement import Environnement


def get_upgrade_rects(largeur, hauteur):
    """Retourne les 3 rectangles cliquables du menu upgrade (mêmes coords que vue_pygame)."""
    boite_largeur = 560
    boite_hauteur = 320
    boite_x = (largeur - boite_largeur) // 2
    boite_y = (hauteur - boite_hauteur) // 2

    rects = []
    for i in range(3):
        yy = boite_y + 95 + i * 65
        rects.append(pygame.Rect(boite_x + 40, yy, 480, 45))
    return rects


def main():
    robot = RobotMobile(moteur=MoteurDifferentiel())
    env = Environnement()
    env.ajouter_robot(robot)

    controleur = ControleurIA(
        v_max=3.0,
        omega_max=3.5,
        seuil_fuite=2.2,
        rayon_influence=4.0,
        distance_attraction_item=3.5,
    )
    controleur.set_environnement(env)

    vue = VuePygame()
    env.reinitialiser()

    running = True
    while running:
        choix_upgrade = None  # sera défini par clic ou touche

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r and env.game_over:
                    env.reinitialiser()

            # --- Clic souris pour choisir une upgrade ---
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if env.en_pause_upgrade:
                    mx, my = event.pos
                    rects = get_upgrade_rects(vue.largeur, vue.hauteur)
                    for i, rect in enumerate(rects):
                        if rect.collidepoint(mx, my):
                            choix_upgrade = i + 1  # 1-indexed
                            break

                elif env.game_over:
                    env.reinitialiser()

        # Commande IA (mouvement + tir uniquement, pas d'upgrade)
        commande = controleur.lire_commande()

        robot.commander(v=commande["v"], omega=commande["omega"])

        dt = vue.tick(60)
        env.mettre_a_jour(
            dt,
            tirer_joueur=commande["tirer"],
            choix_upgrade=choix_upgrade,   # vient du clic joueur
        )

        vue.dessiner_environnement(env)

    pygame.quit()


if __name__ == "__main__":
    main()