# src/test_combat.py
import sys
import glfw # Garder pour la gestion de la fenêtre et des inputs de base si Engine ne le fait pas entièrement
import numpy as np
from OpenGL.GL import * # Garder pour les appels OpenGL directs si nécessaire (ex: clear color)

# Importer les composants principaux du moteur
from engine.window import Window
from engine.core import Engine
from engine.renderer import Renderer
from engine.ecs.world import World
from engine.ui.ui_manager import UIManager # Assumer l'existence d'un UIManager
from engine.input.input_manager import InputManager # Assumer l'existence d'un InputManager

# Importer la scène de démo de combat
from engine.scenes.demo_scene import CombatDemoScene # Utiliser le nom de classe mis à jour

def main():
    window = None # Initialiser à None pour le bloc finally
    try:
        # 1. Initialisation des composants principaux
        print("Initializing engine components...")
        window = Window(width=1280, height=720, title="Combat Demo Scene")
        world = World()
        renderer = Renderer() # Initialisation potentiellement gérée par Engine ou à faire ici
        ui_manager = UIManager(window.window) # UIManager a besoin de la fenêtre GLFW
        input_manager = InputManager(window.window) # InputManager a besoin de la fenêtre GLFW

        # S'assurer que le renderer est prêt (contexte OpenGL, etc.)
        # Ceci pourrait être dans Engine.__init__ ou nécessiter un appel explicite
        # renderer.initialize() # Décommentez si nécessaire

        print("Components initialized.")

        # 2. Création et initialisation de la scène de démo
        print("Creating and initializing CombatDemoScene...")
        # Passer toutes les dépendances nécessaires à la scène
        combat_demo_scene = CombatDemoScene(world, renderer, ui_manager, input_manager)
        # L'initialisation de la scène (création entités, etc.) se fait dans combat_demo_scene.initialize()
        # qui sera appelée par l'Engine lors du changement de scène ou au démarrage.

        print("CombatDemoScene created.")

        # 3. Création de l'Engine et configuration de la scène initiale
        print("Initializing Engine...")
        # L'Engine gère la boucle principale, les mises à jour et le rendu
        engine = Engine(window, renderer, world, ui_manager, input_manager) # Passer les dépendances à l'Engine

        # Définir la scène active
        engine.set_active_scene(combat_demo_scene)
        print("Engine initialized and scene set.")

        # 4. Affichage des instructions utilisateur (si nécessaire)
        print("\n--- Combat Demo Controls ---")
        # Ajouter ici les contrôles spécifiques définis dans demo_ui.py ou player_setup.py
        print("Check the in-game UI for controls and stats.")
        print("Press ESC to exit.")
        print("--------------------------\n")

        # 5. Lancement de la boucle principale du jeu
        print("Starting main loop...")
        engine.run() # Lance la boucle update/render

    except Exception as e:
        print(f"\n--- An error occurred ---")
        import traceback
        traceback.print_exc()
        print(f"Error details: {e}")
        print("-------------------------\n")
        sys.exit(1)

    finally:
        # Nettoyage propre des ressources
        print("Cleaning up resources...")
        if hasattr(engine, 'cleanup'): # Si l'Engine a une méthode cleanup
             engine.cleanup()
        if window:
            window.cleanup()
        print("Cleanup finished. Exiting.")

if __name__ == "__main__":
    main()