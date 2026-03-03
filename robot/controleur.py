from abc import ABC, abstractmethod
import pygame


class Controleur(ABC):

    @abstractmethod
    def lire_commande(self):
        """Retourne une commande pour le robot"""
        pass


class ControleurTerminal(Controleur):

    def lire_commande(self):
        print("Commande differentiel : v omega (ex: 1.0 0.5)")
        entree = input("> ")

        try:
            v_str, omega_str = entree.split()
            v = float(v_str)
            omega = float(omega_str)
        except ValueError:
            print("Commande invalide")
            return {"v": 0.0, "omega": 0.0}

        return {"v": v, "omega": omega}
    
class ControleurClavierPygame(Controleur):
    
    def __init__(self, v_max=2.0, omega_max=2.0):
        self.v_max = v_max
        self.omega_max = omega_max

    def lire_commande(self):
        pygame.event.pump()
        keys = pygame.key.get_pressed()

        v = 0.0
        omega = 0.0

        if keys[pygame.K_UP]:
            v = self.v_max
        if keys[pygame.K_DOWN]:
            v = -self.v_max
        if keys[pygame.K_LEFT]:
            omega = self.omega_max
        if keys[pygame.K_RIGHT]:
            omega = -self.omega_max

        return {"v": v, "omega": omega}