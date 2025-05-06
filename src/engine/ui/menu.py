# src/engine/ui/menu.py
import pygame
import math

# Import UIEvent/UIEventType from ui_base
from .ui_base import UIEvent, UIEventType, get_ui_renderer

# Try to import OpenGL
try:
    from OpenGL.GL import *
    import glm
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("OpenGL not available for MenuManager, using fallback rendering")

# Our simple MainMenu implementation is already in this file
# No need to import it from elsewhere

# Commented out imports that cause issues
# from src.engine.ui.menus.main_menu import MainMenu
# from src.engine.ui.menus.pause_menu import PauseMenu
# from src.engine.ui.character.inventory_menu import InventoryMenu
# from src.engine.ui.character.skill_tree_menu import SkillTreeMenu
# from src.engine.ui.character.character_sheet import CharacterSheet

class MenuManager:
    def __init__(self, game_instance):
        """
        Initialise le gestionnaire de menus.

        Args:
            game_instance: Référence à l'instance principale du jeu (pour accéder à l'état, etc.)
                           Peut être None si le manager est utilisé de manière isolée au début.
        """
        self.game = game_instance
        self.menu_stack = []  # Pile pour gérer les menus ouverts (ex: Pause par-dessus Jeu)
        self.current_transition = None # Pour gérer les animations de transition
        self.screen_width = 0
        self.screen_height = 0
        
        # Debug flag
        self.debug = False

        # Initialiser avec le menu principal si nécessaire (ou laisser le jeu le faire)
        # self.push_menu(MainMenu(self))

    @property
    def is_menu_active(self):
        """Retourne True si un menu est actuellement affiché."""
        return len(self.menu_stack) > 0

    @property
    def is_game_paused(self):
        """
        Détermine si le jeu doit être en pause.
        Typiquement, le jeu est en pause si un menu non-superposé au jeu est actif.
        (ex: Menu Principal, Menu Pause, mais pas forcément un inventaire rapide)
        """
        if not self.is_menu_active:
            return False
        # On considère que le jeu est en pause si le menu actif le demande
        # Par défaut, on peut considérer que tout menu met en pause.
        # On pourrait ajouter une propriété 'pauses_game' aux classes de menu.
        # Exemple simple : Pause si n'importe quel menu est ouvert.
        return True # Simplification: tout menu ouvert met en pause.

    def get_active_menu(self):
        """Retourne le menu actuellement au sommet de la pile."""
        if self.is_menu_active:
            return self.menu_stack[-1]
        return None

    def push_menu(self, menu_instance):
        """Ajoute un nouveau menu au sommet de la pile."""
        # TODO: Gérer les transitions (fade out de l'ancien, fade in du nouveau)
        print(f"Pushing menu: {type(menu_instance).__name__}")
        self.menu_stack.append(menu_instance)
        # Potentiellement notifier le jeu que l'état de pause a changé
        if self.game and hasattr(self.game, 'on_pause_state_change'):
            self.game.on_pause_state_change(self.is_game_paused)

    def pop_menu(self):
        """Retire le menu au sommet de la pile."""
        # TODO: Gérer les transitions
        if self.is_menu_active:
            popped_menu = self.menu_stack.pop()
            print(f"Popping menu: {type(popped_menu).__name__}")
            # Potentiellement notifier le jeu que l'état de pause a changé
            if self.game and hasattr(self.game, 'on_pause_state_change'):
                self.game.on_pause_state_change(self.is_game_paused)
            return popped_menu
        return None

    def clear_stack(self):
        """Vide complètement la pile de menus."""
        print("Clearing menu stack.")
        self.menu_stack.clear()
        # Potentiellement notifier le jeu que l'état de pause a changé
        if self.game and hasattr(self.game, 'on_pause_state_change'):
            self.game.on_pause_state_change(self.is_game_paused)

    def handle_event(self, event):
        """Passe les événements au menu actif."""
        if self.is_menu_active:
            active_menu = self.get_active_menu()
            if active_menu and hasattr(active_menu, 'handle_event'):
                handled = active_menu.handle_event(event)
                if handled:
                    return True # L'événement a été consommé par le menu

        # Gestion globale des raccourcis clavier pour les menus
        if event.type == pygame.KEYDOWN:
            # --- Menu Pause (Echap) ---
            if event.key == pygame.K_ESCAPE:
                if self.game and hasattr(self.game, 'is_in_gameplay') and self.game.is_in_gameplay(): # Vérifier si on est en jeu
                    active_menu = self.get_active_menu()
                    # Commented out to avoid import issues
                    # if isinstance(active_menu, PauseMenu):
                    #     self.pop_menu() # Fermer le menu pause
                    # # Si un menu de personnage est ouvert, Echap le ferme aussi
                    # elif isinstance(active_menu, (InventoryMenu, SkillTreeMenu, CharacterSheet)):
                    #      self.pop_menu()
                    # # Sinon, si aucun menu n'est ouvert, ouvrir le menu pause
                    # elif not self.is_menu_active:
                    #      # Assumer que PauseMenu prend juste 'self' (le manager)
                    #      self.push_menu(PauseMenu(self))
                    return True # L'événement Echap est géré

            # Commented out to avoid import issues
            # # --- Menus Personnage (I, K, C) ---
            # elif self.game and self.game.is_in_gameplay(): # Doit être en jeu pour ces menus
            #     active_menu = self.get_active_menu()

            #     # Touche I: Inventaire
            #     if event.key == pygame.K_i:
            #         if isinstance(active_menu, InventoryMenu):
            #             self.pop_menu() # Fermer si déjà ouvert
            #         elif not self.is_menu_active: # Ouvrir seulement si aucun autre menu n'est actif
            #             # Assumer que game_instance a les refs nécessaires
            #             if hasattr(self.game, 'player_inventory') and hasattr(self.game, 'player_stats'):
            #                 self.push_menu(InventoryMenu(self.game.player_inventory, self.game.player_stats))
            #             else:
            #                 print("Erreur: Références joueur manquantes pour InventoryMenu")
            #         return True # Événement géré

            #     # Touche K: Arbre de Compétences
            #     elif event.key == pygame.K_k:
            #          if isinstance(active_menu, SkillTreeMenu):
            #              self.pop_menu() # Fermer si déjà ouvert
            #          elif not self.is_menu_active:
            #              if hasattr(self.game, 'player_skill_tree') and hasattr(self.game, 'player_stats'):
            #                  self.push_menu(SkillTreeMenu(self.game.player_skill_tree, self.game.player_stats))
            #              else:
            #                  print("Erreur: Références joueur manquantes pour SkillTreeMenu")
            #          return True # Événement géré

            #     # Touche C: Fiche Personnage
            #     elif event.key == pygame.K_c:
            #         if isinstance(active_menu, CharacterSheet):
            #             self.pop_menu() # Fermer si déjà ouvert
            #         elif not self.is_menu_active:
            #              if hasattr(self.game, 'player_stats') and hasattr(self.game, 'player_inventory'):
            #                  self.push_menu(CharacterSheet(self.game.player_stats, self.game.player_inventory))
            #              else:
            #                  print("Erreur: Références joueur manquantes pour CharacterSheet")
            #         return True # Événement géré

        return False # L'événement n'a pas été géré par le système de menu

    def update(self, dt):
        """Met à jour le menu actif et gère les transitions."""
        # TODO: Mettre à jour les transitions si self.current_transition n'est pas None

        active_menu = self.get_active_menu()
        if active_menu and hasattr(active_menu, 'update'):
            active_menu.update(dt)

    def draw(self, screen):
        """Dessine le menu actif."""
        # Update screen dimensions for the renderer
        self.screen_width, self.screen_height = screen.get_size()
        
        # Get UI renderer
        renderer = get_ui_renderer(self.screen_width, self.screen_height)
        
        # Check if we're using OpenGL rendering
        using_opengl = OPENGL_AVAILABLE and renderer is not None
        
        if self.debug:
            print(f"MenuManager draw - using OpenGL: {using_opengl}")
            
        # Draw the active menu
        active_menu = self.get_active_menu()
        if active_menu and hasattr(active_menu, 'draw'):
            active_menu.draw(screen)

# Note: L'instance de MenuManager sera typiquement créée dans la classe principale du jeu (Core ou Game)
# et ses méthodes update, draw, handle_event seront appelées depuis la boucle principale du jeu.

class MainMenu:
    """
    Enhanced main menu implementation with background image and styled buttons
    """
    def __init__(self, width, height, start_callback, quit_callback):
        self.width = width
        self.height = height
        self.start_callback = start_callback
        self.quit_callback = quit_callback
        
        # Initialize menu elements
        self.menu_items = [
            {'text': 'Start Game', 'callback': self.start_callback, 'selected': True},
            {'text': 'Options', 'callback': None, 'selected': False},
            {'text': 'Quit', 'callback': self.quit_callback, 'selected': False}
        ]
        
        # Colors and fonts
        self.bg_color = (10, 10, 25)
        self.title_color = (255, 215, 0)  # Gold
        self.item_color = (200, 200, 200)
        self.selected_color = (255, 255, 255)
        self.selected_bg_color = (80, 80, 160, 180)  # Semi-transparent blue
        self.button_shadow_color = (0, 0, 0, 100)  # Semi-transparent black shadow
        
        # Initialize fonts - try using more stylish fonts if available
        try:
            self.title_font = pygame.font.Font(None, 84)  # Larger title
            self.item_font = pygame.font.Font(None, 42)  # Larger menu items
        except:
            # Fall back to system font if custom font fails
            self.title_font = pygame.font.SysFont(None, 84)
            self.item_font = pygame.font.SysFont(None, 42)
        
        # Title with shadow effect
        self.title_text = "Nightfall Defenders"
        self.title_render = self.title_font.render(self.title_text, True, self.title_color)
        self.title_shadow = self.title_font.render(self.title_text, True, (0, 0, 0))
        self.title_rect = self.title_render.get_rect(center=(width // 2, height // 4))
        self.title_shadow_rect = self.title_shadow.get_rect(center=(width // 2 + 3, height // 4 + 3))
        
        # Initialize textures for OpenGL rendering
        self.bg_texture = 0
        self.title_texture = 0
        self.button_textures = []
        
        # Try to load background image
        self.bg_image = None
        try:
            self.bg_image = pygame.image.load("assets/backgrounds/demo_bg.png").convert_alpha()
            self.bg_image = pygame.transform.scale(self.bg_image, (width, height))
            
            # Create OpenGL texture if available
            renderer = get_ui_renderer(width, height)
            if OPENGL_AVAILABLE and renderer is not None:
                self.bg_texture = renderer.create_texture_from_surface(self.bg_image)
                self.title_texture = renderer.create_texture_from_surface(self.title_render)
        except Exception as e:
            print(f"Could not load background image: {e}")
        
        # Try to load button image
        self.button_image = None
        try:
            self.button_image = pygame.image.load("assets/ui/button.png").convert_alpha()
            # Default size, will be scaled per button
            self.button_width = 240
            self.button_height = 60
        except Exception as e:
            print(f"Could not load button image: {e}")
            
        # Animation variables
        self.animation_time = 0
        self.pulse_rate = 2.0  # Pulses per second
            
        # Selected item index
        self.selected_index = 0
        
    def handle_event(self, event):
        """Handle menu navigation and selection"""
        if event.type == pygame.KEYDOWN:
            # Navigate up/down
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.menu_items)
                return True
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.menu_items)
                return True
            # Select item
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                callback = self.menu_items[self.selected_index]['callback']
                if callback:
                    callback()
                return True
        return False
        
    def update(self, dt):
        """Update menu animations"""
        self.animation_time += dt
        # Apply pulsing effect to selected item
        pulse_value = (math.sin(self.animation_time * self.pulse_rate * math.pi) + 1) / 2  # Value between 0 and 1
        
        # Update selected state based on selected_index
        for i, item in enumerate(self.menu_items):
            item['selected'] = (i == self.selected_index)
            
    def draw(self, screen):
        """Draw the menu with OpenGL or PyGame"""
        # Get UI renderer
        renderer = get_ui_renderer(self.width, self.height)
        using_opengl = OPENGL_AVAILABLE and renderer is not None
            
        # Draw background
        if using_opengl:
            if self.bg_texture:
                renderer.draw_texture(self.bg_texture, 0, 0, self.width, self.height)
            else:
                # Draw solid color background
                renderer.draw_rectangle(0, 0, self.width, self.height, self.bg_color)
        
            # Draw title with shadow
            if self.title_texture:
                # Draw shadow
                shadow_offset = 3
                renderer.draw_texture(
                    self.title_texture, 
                    self.title_rect.x + shadow_offset, 
                    self.title_rect.y + shadow_offset, 
                    self.title_rect.width, 
                    self.title_rect.height, 
                    (0, 0, 0, 200)  # Dark shadow color
                )
                
                # Draw title
                renderer.draw_texture(
                    self.title_texture,
                    self.title_rect.x,
                    self.title_rect.y,
                    self.title_rect.width,
                    self.title_rect.height
                )
        
        # Draw menu items
        for i, item in enumerate(self.menu_items):
                # Calculate position
                y_pos = self.height // 2 + i * 60
                
                # Draw button background
                if item['selected']:
                    # Selected item has different background
                    renderer.draw_rectangle(
                        self.width // 2 - self.button_width // 2,
                        y_pos,
                        self.button_width,
                        self.button_height,
                        self.selected_bg_color
                    )
                    text_color = self.selected_color
                else:
                    # Normal item background
                    renderer.draw_rectangle(
                        self.width // 2 - self.button_width // 2,
                        y_pos,
                        self.button_width,
                        self.button_height,
                        (40, 40, 80, 180)  # Semi-transparent dark blue
                    )
                    text_color = self.item_color
                    
                # Draw text
                text_surface = self.item_font.render(item['text'], True, text_color)
                text_width, text_height = text_surface.get_size()
                text_x = self.width // 2 - text_width // 2
                text_y = y_pos + self.button_height // 2 - text_height // 2
                
                # Create texture for text if needed
                text_texture = renderer.create_texture_from_surface(text_surface)
                renderer.draw_texture(
                    text_texture,
                    text_x,
                    text_y,
                    text_width,
                    text_height
                )
        else:
            # PyGame fallback rendering
            
            # Draw background
            if self.bg_image:
                screen.blit(self.bg_image, (0, 0))
            else:
                screen.fill(self.bg_color)
                
            # Draw title with shadow
            screen.blit(self.title_shadow, self.title_shadow_rect)
            screen.blit(self.title_render, self.title_rect)
            
            # Draw menu items
            for i, item in enumerate(self.menu_items):
                # Calculate position
                y_pos = self.height // 2 + i * 60
                
                # Draw button background
                button_rect = pygame.Rect(
                    self.width // 2 - self.button_width // 2,
                    y_pos,
                    self.button_width,
                    self.button_height
                )
                
                if item['selected']:
                    # Selected item
                    s = pygame.Surface((self.button_width, self.button_height), pygame.SRCALPHA)
                    s.fill(self.selected_bg_color)
                    screen.blit(s, button_rect)
                    text_color = self.selected_color
                else:
                    # Normal item
                    s = pygame.Surface((self.button_width, self.button_height), pygame.SRCALPHA)
                    s.fill((40, 40, 80, 180))  # Semi-transparent dark blue
                    screen.blit(s, button_rect)
                    text_color = self.item_color
                
                # Draw text
                text_surface = self.item_font.render(item['text'], True, text_color)
                text_rect = text_surface.get_rect(center=button_rect.center)
                screen.blit(text_surface, text_rect)