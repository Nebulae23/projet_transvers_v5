# src/engine/scenes/ui_demo/ui_demo_environment.py

import pygame

from src.engine.ecs.world import World

class UIDemoEnvironment:
    """
    Représente un environnement minimal pour la scène de démonstration UI.
    Peut contenir des éléments de décor ou des entités non interactives.
    """
    def __init__(self, world: World):
        self.world = world
        # Initialiser des éléments d'environnement si nécessaire
        # Par exemple, créer des entités pour le décor
        print("UIDemoEnvironment initialized.")

    def update(self, dt: float):
        # Mettre à jour l'état de l'environnement si nécessaire
        pass

    def render(self, screen: pygame.Surface):
        # Dessiner des éléments de l'environnement (ex: fond, décor)
        # Pour l'instant, on ne dessine rien de spécifique ici,
        # la scène principale gère le fond.
        pass