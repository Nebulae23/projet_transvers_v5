# src/test_ui_demo.py

import pygame
import sys
import random

from src.engine.core import GameEngine  # Supposant une classe GameEngine ou similaire
from src.engine.ecs.world import World
from src.engine.input.input_manager import InputManager
from src.engine.scenes.ui_demo.ui_demo_scene import UIDemoScene
from src.engine.ecs.components import Stats, Health, Inventory # Ajoutez d'autres composants si nécessaire

# --- Configuration ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# --- Initialisation ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("UI Demo Scene Test")
clock = pygame.time.Clock()

# Initialisation des systèmes principaux
world = World()
input_manager = InputManager()

# Création de la scène de démo UI
# Note: La scène crée son propre joueur de test et environnement
ui_demo_scene = UIDemoScene(screen, input_manager, world)

# --- Commandes de Test ---
def register_test_commands():
    print("Registering test commands...")
    # Ouvrir/Fermer les menus
    input_manager.register_key_action(pygame.K_i, ui_demo_scene.toggle_inventory, on_press=True)
    input_manager.register_key_action(pygame.K_c, ui_demo_scene.toggle_character_sheet, on_press=True)
    input_manager.register_key_action(pygame.K_k, ui_demo_scene.toggle_skill_tree, on_press=True)
    input_manager.register_key_action(pygame.K_u, ui_demo_scene.toggle_upgrade_menu, on_press=True)
    input_manager.register_key_action(pygame.K_o, ui_demo_scene.toggle_options_menu, on_press=True)
    input_manager.register_key_action(pygame.K_ESCAPE, ui_demo_scene.toggle_pause_menu, on_press=True)
    print("Menu toggle keys registered (I, C, K, U, O, ESC).")

    # Modifier les stats du joueur (Exemple : Augmenter la force)
    def increase_strength():
        player_entity = ui_demo_scene.player.entity
        stats = world.get_component(player_entity, Stats)
        if stats:
            stats.strength += 1
            print(f"Player strength increased to: {stats.strength}")
        else:
            print("Player Stats component not found.")
    input_manager.register_key_action(pygame.K_F1, increase_strength, on_press=True)
    print("Stat modification key registered (F1 for Strength+).")

    # Modifier la vie du joueur (Exemple: Prendre des dégâts)
    def take_damage():
        player_entity = ui_demo_scene.player.entity
        health = world.get_component(player_entity, Health)
        if health:
            damage = random.randint(5, 15)
            health.current = max(0, health.current - damage)
            print(f"Player took {damage} damage. Current health: {health.current}/{health.max_value}")
        else:
            print("Player Health component not found.")
    input_manager.register_key_action(pygame.K_F2, take_damage, on_press=True)
    print("Damage simulation key registered (F2).")

    # Générer un item de test dans l'inventaire
    def add_test_item():
        player_entity = ui_demo_scene.player.entity
        inventory = world.get_component(player_entity, Inventory)
        if inventory:
            item_id = f"test_item_{random.randint(100, 999)}"
            new_item = {"id": item_id, "quantity": 1, "name": f"Test Item {item_id.split('_')[-1]}"} # Ajout d'un nom pour l'affichage
            inventory.items.append(new_item)
            print(f"Added item '{new_item['name']}' to inventory.")
        else:
            print("Player Inventory component not found.")
    input_manager.register_key_action(pygame.K_F3, add_test_item, on_press=True)
    print("Item generation key registered (F3).")

    # Simuler un événement (Exemple : Gain d'XP)
    def gain_xp():
        player_entity = ui_demo_scene.player.entity
        stats = world.get_component(player_entity, Stats)
        if stats:
            xp_gain = random.randint(20, 50)
            stats.xp += xp_gain
            print(f"Player gained {xp_gain} XP. Current XP: {stats.xp}/{stats.xp_to_next_level}")
            # Ajouter ici la logique de montée de niveau si nécessaire
            if stats.xp >= stats.xp_to_next_level:
                 print("Level Up!") # Simplifié
                 stats.level += 1
                 stats.xp -= stats.xp_to_next_level
                 stats.xp_to_next_level = int(stats.xp_to_next_level * 1.5) # Exemple simple
                 skills = world.get_component(player_entity, Skills)
                 if skills:
                     skills.available_points +=1
                     print(f"Gained 1 skill point. Total: {skills.available_points}")

        else:
            print("Player Stats component not found.")
    input_manager.register_key_action(pygame.K_F4, gain_xp, on_press=True)
    print("XP gain simulation key registered (F4).")


register_test_commands()

# --- Boucle Principale ---
running = True
while running:
    dt = clock.tick(FPS) / 1000.0  # Delta time en secondes

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Passer l'événement à l'InputManager d'abord
        input_manager.handle_event(event)
        # Ensuite, passer l'événement à la scène active pour la gestion UI/spécifique
        ui_demo_scene.handle_event(event)

    # Mise à jour
    input_manager.update() # Traiter les actions enregistrées
    ui_demo_scene.update(dt)

    # Rendu
    ui_demo_scene.render() # La scène gère le rendu de ses éléments

    pygame.display.flip()

# --- Nettoyage ---
pygame.quit()
sys.exit()