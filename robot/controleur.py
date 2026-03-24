from abc import ABC, abstractmethod
import pygame


class Controleur(ABC):

    @abstractmethod
    def lire_commande(self):
        pass


class ControleurTerminal(Controleur):

    def lire_commande(self):
        return {
            "v": 0.0,
            "omega": 0.0,
            "tirer": False,
            "recommencer": False,
            "choix_upgrade": None
        }


class ControleurClavierPygame(Controleur):

    def __init__(self, v_max=3.0, omega_max=3.0):
        self.v_max = v_max
        self.omega_max = omega_max

    def lire_commande(self):
        pygame.event.pump()
        keys = pygame.key.get_pressed()

        v = 0.0
        omega = 0.0

        if keys[pygame.K_UP] or keys[pygame.K_z] or keys[pygame.K_w]:
            v = self.v_max
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            v = -self.v_max
        if keys[pygame.K_LEFT] or keys[pygame.K_q] or keys[pygame.K_a]:
            omega = self.omega_max
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            omega = -self.omega_max

        tirer = keys[pygame.K_SPACE]
        recommencer = keys[pygame.K_r]

        choix_upgrade = None
        if keys[pygame.K_1]:
            choix_upgrade = 1
        elif keys[pygame.K_2]:
            choix_upgrade = 2
        elif keys[pygame.K_3]:
            choix_upgrade = 3

        return {
            "v": v,
            "omega": omega,
            "tirer": tirer,
            "recommencer": recommencer,
            "choix_upgrade": choix_upgrade
        }