import pygame
import math
from ..ecs.components.transform import Transform
from ..ecs.components.player_controller import PlayerController

class PlayerSystem:
    """
    Système responsable de la mise à jour des entités joueur
    en fonction des entrées utilisateur.
    """
    def __init__(self):
        pass

    def update(self, dt, world, input_manager):
        """
        Met à jour toutes les entités avec un PlayerController.

        Args:
            dt (float): Le temps écoulé depuis la dernière frame.
            world (World): L'instance du monde ECS.
            input_manager (InputManager): Le gestionnaire d'entrées.
        """
        for entity_id, (controller, transform) in world.get_components(PlayerController, Transform):
            # Réinitialiser les actions avant de traiter les nouvelles entrées
            controller.reset_actions()

            # --- Gestion des déplacements ---
            controller.move_left = input_manager.is_key_pressed(pygame.K_q) or input_manager.is_key_pressed(pygame.K_LEFT)
            controller.move_right = input_manager.is_key_pressed(pygame.K_d) or input_manager.is_key_pressed(pygame.K_RIGHT)
            controller.move_up = input_manager.is_key_pressed(pygame.K_z) or input_manager.is_key_pressed(pygame.K_UP)
            controller.move_down = input_manager.is_key_pressed(pygame.K_s) or input_manager.is_key_pressed(pygame.K_DOWN)

            move_vector = pygame.Vector2(0, 0)
            if controller.move_left:
                move_vector.x -= 1
            if controller.move_right:
                move_vector.x += 1
            if controller.move_up:
                move_vector.y -= 1 # Pygame a l'axe Y inversé (haut = négatif)
            if controller.move_down:
                move_vector.y += 1

            # Normaliser pour éviter un déplacement diagonal plus rapide
            if move_vector.length_squared() > 0: # Vérifier si le vecteur n'est pas nul
                move_vector = move_vector.normalize()

            # Appliquer le déplacement
            transform.position += move_vector * controller.speed * dt

            # --- Gestion des attaques ---
            if input_manager.is_mouse_button_pressed(1): # Clic gauche
                controller.attack = True
                # Ici, on pourrait déclencher un événement d'attaque ou interagir
                # avec le système de combat. Pour l'instant, on met juste le flag.
                # print(f"Player {entity_id} attacking!") # Pour le débogage

            # --- Gestion des capacités ---
            if input_manager.is_key_pressed(pygame.K_1):
                controller.use_ability_1 = True
                # print(f"Player {entity_id} using ability 1!") # Pour le débogage
            if input_manager.is_key_pressed(pygame.K_2):
                controller.use_ability_2 = True
                # print(f"Player {entity_id} using ability 2!") # Pour le débogage

            # Note : Les actions comme l'attaque et les capacités sont définies comme True
            # pendant la frame où elles sont activées. D'autres systèmes (CombatSystem, AbilitySystem)
            # devront lire cet état et agir en conséquence, puis potentiellement
            # le remettre à False ou gérer des cooldowns. La méthode reset_actions()
            # au début de l'update garantit que l'état n'est actif que pour une frame
            # si aucun autre système ne le maintient.