import pygame

from abc import ABC, abstractmethod
class Controleur(ABC):
    @abstractmethod
    def lire_commande(self):
        """Retourne une commande pour le robot"""
        pass
class ControleurTerminal(Controleur):
    def lire_commande(self):
        print("Commande differentiel : v omega (ex: 1.0 0.5)")

        entree = input("> ")
        v_str, omega_str = entree.split()

        v = float(v_str)
        omega = float(omega_str)

        return {"v": v, "omega": omega}

class ControleurClavierPygame(Controleur):
    def __init__(self, v_max=1.0, omega_max=1.0):
        self.v_max = float(v_max)
        self.omega_max = float(omega_max)

    def lire_commande(self):
        # Important: traiter les events, sinon la fenêtre freeze
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return {"quit": True}

        keys = pygame.key.get_pressed()

        v = 0.0
        omega = 0.0

        # Avance / recule
        if keys[pygame.K_UP]:
            v += self.v_max
        if keys[pygame.K_DOWN]:
            v -= self.v_max

        # Rotation gauche / droite
        if keys[pygame.K_LEFT]:
            omega += self.omega_max
        if keys[pygame.K_RIGHT]:
            omega -= self.omega_max

        # Quitter aussi au clavier
        if keys[pygame.K_ESCAPE]:
            return {"quit": True}

        return {"v": v, "omega": omega}