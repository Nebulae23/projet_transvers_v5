# src/engine/scenes/ui_demo/ui_demo_scene.py

import pygame

from src.engine.scenes.scene import Scene
from src.engine.ecs.world import World
from src.engine.input.input_manager import InputManager
from src.engine.ui.hud.hud import HUD
from src.engine.ui.menus.main_menu import MainMenu
from src.engine.ui.menus.pause_menu import PauseMenu
from src.engine.ui.character.character_sheet import CharacterSheet
from src.engine.ui.character.inventory_menu import InventoryMenu
from src.engine.ui.character.skill_tree_menu import SkillTreeMenu
from src.engine.ui.ability_upgrade.upgrade_menu import UpgradeMenu
from src.engine.ui.options.options_menu import OptionsMenu

from .ui_test_player import UITestPlayer
from .ui_demo_environment import UIDemoEnvironment

class UIDemoScene(Scene):
    """
    Scène de démonstration pour l'interface utilisateur.
    Montre l'intégration des différents composants UI.
    """
    def __init__(self, screen: pygame.Surface, input_manager: InputManager, world: World):
        super().__init__(screen, input_manager, world)
        self.player = UITestPlayer(world)
        self.environment = UIDemoEnvironment(world)

        # Initialisation des composants UI
        self.hud = HUD(screen, world, self.player.entity) # Assurez-vous que HUD peut prendre l'entité joueur
        self.main_menu = MainMenu(screen, input_manager) # Adaptez si nécessaire
        self.pause_menu = PauseMenu(screen, input_manager)
        self.character_sheet = CharacterSheet(screen, input_manager, world, self.player.entity)
        self.inventory_menu = InventoryMenu(screen, input_manager, world, self.player.entity)
        self.skill_tree_menu = SkillTreeMenu(screen, input_manager, world, self.player.entity)
        self.upgrade_menu = UpgradeMenu(screen, input_manager, world, self.player.entity)
        self.options_menu = OptionsMenu(screen, input_manager) # Adaptez si nécessaire

        # État initial des menus
        self.active_menu = None # Aucun menu actif au début, seulement le HUD
        self.menus = {
            "inventory": self.inventory_menu,
            "character": self.character_sheet,
            "skills": self.skill_tree_menu,
            "upgrades": self.upgrade_menu,
            "options": self.options_menu,
            "pause": self.pause_menu,
            # "main": self.main_menu # Le menu principal est généralement géré différemment
        }
        # Ordre dans lequel les menus apparaissent avec TAB
        self.menu_cycle_order = [
            None, # Représente l'état "aucun menu ouvert" (juste le HUD)
            self.inventory_menu,
            self.character_sheet,
            self.skill_tree_menu,
            self.upgrade_menu,
            self.options_menu,
            self.pause_menu
        ]
        self.current_menu_index = 0 # Commence avec aucun menu ouvert

        # Enregistrement des gestionnaires d'événements UI (simplifié)
        self._register_event_handlers()

    def _register_event_handlers(self):
        """Enregistre les gestionnaires d'événements pour les contrôles de la démo."""
        # Enregistrement des touches individuelles (conservé pour accès direct)
        # Ces appels sont maintenant redondants si test_ui_demo.py les enregistre déjà,
        # mais laissés ici pour montrer la structure complète de la scène.
        # Dans une implémentation finale, on choisirait où centraliser l'enregistrement.
        # self.input_manager.register_key_action(pygame.K_i, self.toggle_inventory, on_press=True)
        # self.input_manager.register_key_action(pygame.K_c, self.toggle_character_sheet, on_press=True)
        # self.input_manager.register_key_action(pygame.K_k, self.toggle_skill_tree, on_press=True)
        # self.input_manager.register_key_action(pygame.K_u, self.toggle_upgrade_menu, on_press=True)
        # self.input_manager.register_key_action(pygame.K_o, self.toggle_options_menu, on_press=True)
        # self.input_manager.register_key_action(pygame.K_ESCAPE, self.toggle_pause_menu, on_press=True)

        # Enregistrement de la touche TAB pour cycler entre les menus
        # Assurez-vous que cette ligne n'est pas dupliquée dans test_ui_demo.py
        if not self.input_manager.is_key_registered(pygame.K_TAB):
             self.input_manager.register_key_action(pygame.K_TAB, self.cycle_menu, on_press=True)
             print("UI Demo Scene: Registered TAB key for menu cycling.")


    def set_active_menu(self, menu):
        """Définit le menu actif et gère son état show/hide."""
        if self.active_menu and hasattr(self.active_menu, 'hide'):
            try:
                self.active_menu.hide() # Cache l'ancien menu s'il existe
            except Exception as e:
                print(f"Error hiding menu {self.active_menu.__class__.__name__}: {e}")


        self.active_menu = menu
        if menu in self.menu_cycle_order:
           self.current_menu_index = self.menu_cycle_order.index(menu)
        # else: Gérer le cas où un menu non cyclable est activé (ex: MainMenu)

        if self.active_menu and hasattr(self.active_menu, 'show'):
            try:
               self.active_menu.show() # Affiche le nouveau menu
            except Exception as e:
                print(f"Error showing menu {self.active_menu.__class__.__name__}: {e}")


    def cycle_menu(self):
        """Passe au menu suivant dans l'ordre défini."""
        self.current_menu_index = (self.current_menu_index + 1) % len(self.menu_cycle_order)
        next_menu = self.menu_cycle_order[self.current_menu_index]
        self.set_active_menu(next_menu)
        if next_menu:
            print(f"Cycled to menu: {next_menu.__class__.__name__}")
        else:
            print("Cycled to game view (no menu active).")


    def toggle_inventory(self):
        if self.active_menu == self.inventory_menu:
            self.set_active_menu(None)
        else:
            self.set_active_menu(self.inventory_menu)

    def toggle_character_sheet(self):
        if self.active_menu == self.character_sheet:
            self.set_active_menu(None)
        else:
            self.set_active_menu(self.character_sheet)

    def toggle_skill_tree(self):
        if self.active_menu == self.skill_tree_menu:
            self.set_active_menu(None)
        else:
            self.set_active_menu(self.skill_tree_menu)

    def toggle_upgrade_menu(self):
         if self.active_menu == self.upgrade_menu:
            self.set_active_menu(None)
         else:
            self.set_active_menu(self.upgrade_menu)

    def toggle_options_menu(self):
        if self.active_menu == self.options_menu:
            self.set_active_menu(None)
        else:
            self.set_active_menu(self.options_menu)

    def toggle_pause_menu(self):
        # Le menu pause est souvent prioritaire ou différent
        if self.active_menu == self.pause_menu:
            # Si on est dans le menu pause, on le ferme (retour au jeu/HUD)
            self.set_active_menu(None)
        else:
            # Si un autre menu est ouvert ou si on est en jeu, on ouvre le menu pause
            self.set_active_menu(self.pause_menu)


    def update(self, dt: float):
        self.world.update(dt)
        self.player.update(dt) # Mettre à jour le joueur de test si nécessaire
        self.environment.update(dt) # Mettre à jour l'environnement de test si nécessaire

        # Mettre à jour le monde et les entités seulement si le jeu n'est pas "en pause"
        # par un menu comme PauseMenu ou OptionsMenu (à adapter selon les besoins)
        game_paused = self.active_menu in [self.pause_menu, self.options_menu] # Exemple

        if not game_paused:
            self.world.update(dt)
            self.player.update(dt)
            self.environment.update(dt)

        # Mettre à jour le menu actif s'il y en a un
        if self.active_menu:
            self.active_menu.update(dt)

        # Le HUD est généralement toujours mis à jour, sauf peut-être dans le MainMenu
        if self.active_menu != self.main_menu: # Assurez-vous que main_menu existe si utilisé ici
            self.hud.update(dt)

    def render(self):
        self.screen.fill((0, 0, 20)) # Fond simple pour la démo

        # Rendu de l'environnement minimal si nécessaire
        self.environment.render(self.screen)

        # Rendu du joueur de test si nécessaire
        self.player.render(self.screen)

        # Rendu du HUD (toujours visible, sauf si menu principal)
        if self.active_menu != self.main_menu:
             self.hud.render()

        # Rendu du menu actif
        if self.active_menu:
            self.active_menu.render()

    def handle_event(self, event: pygame.event.Event):
        # 1. Donner la priorité à l'InputManager global pour les raccourcis (TAB, ESC, F1-F4 etc.)
        #    handle_event retourne True s'il a traité l'événement (une action a été déclenchée)
        processed_by_input_manager = self.input_manager.handle_event(event)

        # 2. Si l'InputManager n'a PAS traité l'événement ET qu'un menu est actif,
        #    passer l'événement au menu actif.
        if not processed_by_input_manager and self.active_menu:
            processed_by_menu = self.active_menu.handle_event(event)
            # Si le menu a traité l'événement, on s'arrête là en général.
            if processed_by_menu:
                return

        # 3. Si l'événement n'a été traité ni par l'InputManager ni par un menu actif,
        #    on peut le passer au HUD (pour clics sur minimap, etc.)
        #    OU au joueur si aucun menu n'est actif (pour les mouvements, etc.)
        if not processed_by_input_manager:
            # Le HUD peut avoir besoin de certains events même si un menu est ouvert (ex: tooltips survolés)
            # ou seulement quand aucun menu n'est ouvert. À adapter.
            # Pour la démo, on le laisse écouter.
            processed_by_hud = self.hud.handle_event(event)
            if processed_by_hud:
                return

            # Si aucun menu n'est actif, passer au joueur
            if not self.active_menu:
                self.player.handle_event(event)