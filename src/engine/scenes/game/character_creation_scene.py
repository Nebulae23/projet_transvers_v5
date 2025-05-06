# src/engine/scenes/game/character_creation_scene.py

import pygame
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Callable
import os
import math

from ..scene import Scene
from ...combat.character_classes import CharacterClass, CharacterClassManager, ClassStats, Character
from ...combat.ability_system import AbilityType, Ability
from ...ecs.world import World
from ...ecs.components import Transform, Sprite
import pygame.font

# Import the UI renderer
from ...ui.ui_base import get_ui_renderer, OPENGL_AVAILABLE

# Try to import HD2DRenderer
try:
    from ...graphics.hd2d_renderer import HD2DRenderer
    HD2D_AVAILABLE = True
except ImportError:
    HD2D_AVAILABLE = False

# Try to import procedural generator
try:
    from ...rendering.procedural_generator import ProceduralGenerator
    PROCEDURAL_AVAILABLE = True
except ImportError:
    PROCEDURAL_AVAILABLE = False

class CharacterCreationScene(Scene):
    """
    Character creation scene.
    Allows players to create and customize their character before starting the game.
    """
    def __init__(self, world: World, renderer, ui_manager, on_character_created=None):
        """
        Initialize the character creation scene.
        
        Args:
            world (World): The ECS world instance.
            renderer (Renderer): The renderer instance.
            ui_manager (UIManager): The UI manager instance.
            on_character_created (callable): Callback when character creation is complete.
        """
        super().__init__(world, renderer, ui_manager)
        
        # Get OpenGL UI renderer if available
        self.ui_renderer = get_ui_renderer(renderer.width, renderer.height)
        self.using_opengl = OPENGL_AVAILABLE and self.ui_renderer is not None
        
        # Disable debug output for the UI renderer
        if self.using_opengl and hasattr(self.ui_renderer, 'debug'):
            self.ui_renderer.debug = False
            print(f"Character Creation Scene using OpenGL UI renderer: {self.using_opengl}")
        
        # Callback when character creation is complete
        self.on_character_created = on_character_created
        self.ui_manager = ui_manager
        
        # Character class manager to get class information
        self.class_manager = CharacterClassManager()
        
        # Navigation and UI buttons
        self.navigation_buttons = {}
        
        # Control buttons for confirmation and actions
        self.control_buttons = []
        
        # Input state tracking
        self.active_tab = "appearance"  # appearance/attributes/abilities
        self.selected_option = 0
        self.input_cooldown = 0.0
        
        # Character preview components
        self.preview_surface = None
        self.character_sprite = None
        self.preview_entity_id = None
        
        # Procedural generator for character appearance
        self.procedural_generator = None
        self.assets_generated = False
        
        # Total ability points to distribute
        self.total_ability_points = 15
        self.available_ability_points = self.total_ability_points
        
        # Attribute points to distribute
        self.available_attribute_points = 15
        
        # Define UI regions dictionary
        self.ui_regions = {}
        
        # Add UI regions
        screen_width = renderer.width
        screen_height = renderer.height
        footer_height = 80
        self.ui_regions["navigation"] = pygame.Rect(0, screen_height - footer_height, screen_width, footer_height)
        
        # Initialize fonts
        self.title_font = pygame.font.SysFont(None, 48)
        self.heading_font = pygame.font.SysFont(None, 36)
        self.text_font = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 18)
        
        # Character creation state
        self.current_step = "class"  # class, appearance, attributes, abilities, summary
        self.character_data = {
            "name": "Hero",
            "gender": "male",  # male/female
            "class": None,  # Will be set to a class dictionary when selected
            "appearance": {
                "skin_tone": 0,  # 0-3 (pale to dark)
                "hair_style": 0,  # 0-5 (different styles)
                "hair_color": 0,  # 0-5 (blonde, brown, black, red, etc.)
                "face_style": 0,  # 0-3 (different face shapes/features)
                "body_type": 0,   # 0-2 (average, muscular, thin)
            },
            "attributes": {
                "strength": 8,
                "dexterity": 8,
                "intelligence": 8,
                "vitality": 8,
                "charisma": 8
            },
            "abilities": {},
            "background": None,
            "equipment": {}
        }
        
        # Initialize class and options lists
        self.available_classes = []
        self.ability_options = []
        self.appearance_options = []
        self.attribute_options = []
        self.background_options = []
        
        # Initialize the scene
        self.initialize()
        
    def initialize(self):
        """
        Initialize the character creation scene.
        Called once when the scene is first loaded.
        """
        print("Initializing Character Creation Scene")
        
        # Load available character classes
        self._load_character_classes()
        
        # Load available backgrounds
        self._load_backgrounds()
        
        # Initialize UI elements
        self._init_ui()
        
        # Create preview character
        self._create_preview_character()
        
        # Set up initial step
        self._setup_class_selection()
        
    def _load_character_classes(self):
        """Load available character classes from the CharacterClass enum."""
        self.available_classes = []
        
        # Get all classes from the CharacterClass enum
        for char_class in CharacterClass:
            # Get the class data from the class manager
            class_stats, class_visuals = self.class_manager.classes[char_class]
            
            # Create class descriptions based on actual abilities and gameplay style
            description = ""
            specialties = []
            difficulty = 2  # Default medium difficulty
            
            if char_class == CharacterClass.SPELLBLADE:
                description = "A versatile warrior who combines sword fighting with arcane magic. Specializes in close-quarters combat with magical enhancements."
                specialties = ["Melee Combat", "Arcane Enhancement", "Balanced Stats"]
                difficulty = 2  # Medium difficulty
            
            elif char_class == CharacterClass.SHADOWMAGE:
                description = "A master of forbidden shadow magic who excels at dealing massive damage and inflicting debilitating effects on enemies."
                specialties = ["Shadow Magic", "Damage Over Time", "Area Effects"]
                difficulty = 3  # Hard difficulty
            
            elif char_class == CharacterClass.BEASTMASTER:
                description = "A primal warrior with a deep connection to nature. Can summon animal companions and harness natural forces in battle."
                specialties = ["Pet Summoning", "Nature Magic", "Versatile Combat"]
                difficulty = 2  # Medium difficulty
            
            elif char_class == CharacterClass.TIMEMAGE:
                description = "A manipulator of the temporal fabric who can alter the flow of time to hinder enemies and bolster allies."
                specialties = ["Time Manipulation", "Support Magic", "Control Effects"]
                difficulty = 3  # Hard difficulty
            
            # Format specialties into a readable string
            specialties_text = ", ".join(specialties)
            
            # Create a complete description
            full_description = f"{description}\n\nSpecialties: {specialties_text}"
            
            # Add the class to the available classes list
            self.available_classes.append({
                "id": char_class.value,
                "enum": char_class,
                "name": char_class.value.capitalize(),
                "description": full_description,
                "stats": class_stats,
                "visuals": class_visuals,
                "main_color": class_visuals.main_color,
                "accent_color": class_visuals.accent_color,
                "specialties": specialties,
                "difficulty": difficulty
            })
        
        print(f"Loaded {len(self.available_classes)} character classes")
        
    def _load_backgrounds(self):
        """Load available character backgrounds."""
        # In a real implementation, these would be loaded from a data file
        # For now, just use some predefined backgrounds
        self.background_options = [
            {
                "id": "street_urchin", 
                "name": "Street Urchin", 
                "description": "You grew up on the streets, learning to survive by your wits. +1 to Dexterity, knowledge of criminal networks, and better prices from shady merchants."
            },
            {
                "id": "noble", 
                "name": "Noble", 
                "description": "Born to privilege, you've had the best education but little real-world experience. +1 to Intelligence, access to high society, and better prices from reputable merchants."
            },
            {
                "id": "soldier", 
                "name": "Soldier", 
                "description": "You've served in the military, trained in discipline and combat. +1 to Strength, better relations with guards, and occasional combat advantage against military foes."
            },
            {
                "id": "scholar", 
                "name": "Scholar", 
                "description": "You've spent years studying arcane knowledge in prestigious academies. +1 to Intelligence, access to rare knowledge, and occasional insights into magical puzzles."
            },
            {
                "id": "merchant", 
                "name": "Merchant", 
                "description": "Your family runs a trading business, and you've learned the art of negotiation. +1 to Charisma, better prices on goods, and occasional unique items from trade networks."
            }
        ]
        
    def _init_ui(self):
        """Initialize UI elements."""
        # Initialize UI regions
        screen_width = self.renderer.width
        screen_height = self.renderer.height
        
        # Create UI regions
        margin = 20
        
        # Header region (banner at top)
        header_height = 60  # Reduced from 80
        self.ui_regions["header"] = pygame.Rect(0, 0, screen_width, header_height)
        
        # Content region (main content area)
        content_width = screen_width
        content_height = screen_height - header_height - 80  # Leave room for footer
        self.ui_regions["content"] = pygame.Rect(0, header_height, content_width, content_height)
        
        # Tab region (where the tabs go, top portion of content)
        tab_height = 50
        self.ui_regions["tabs"] = pygame.Rect(margin, header_height, content_width - margin * 2, tab_height)
        
        # Footer region (for navigation buttons)
        footer_height = 80
        self.ui_regions["footer"] = pygame.Rect(0, screen_height - footer_height, screen_width, footer_height)
        
        # Calculate main content area (where tab content goes)
        main_content_x = margin
        main_content_y = header_height + tab_height + margin
        main_content_width = screen_width - margin * 2  # Use full width minus margins
        main_content_height = content_height - tab_height - margin * 2
        self.ui_regions["main_content"] = pygame.Rect(main_content_x, main_content_y, main_content_width, main_content_height)
        
        # Preview region (for character preview) - centered and smaller
        preview_width = 150
        preview_height = 300
        preview_x = (screen_width - preview_width) // 2
        preview_y = main_content_y + 20
        self.ui_regions["preview"] = pygame.Rect(preview_x, preview_y, preview_width, preview_height)
        
        # Remove info region as we're integrating it into the tabs
        
        # Create and initialize preview surface
        self.preview_surface = pygame.Surface((150, 300))
        self.preview_surface.fill((40, 40, 60))  # Dark blue-gray background
        
        # Create a placeholder character sprite
        self.character_sprite = None
        self.assets_generated = False
        
        # Set up scrollable content
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Navigation buttons
        self.navigation_buttons = {}
        footer_center = self.ui_regions["footer"].centerx
        footer_button_width = 150
        footer_button_height = 40
        footer_button_y = self.ui_regions["footer"].y + (self.ui_regions["footer"].height - footer_button_height) // 2
        
        # Previous button
        prev_button_x = footer_center - footer_button_width - 100
        self.navigation_buttons["prev"] = pygame.Rect(prev_button_x, footer_button_y, footer_button_width, footer_button_height)
        
        # Next button
        next_button_x = footer_center + 100
        self.navigation_buttons["next"] = pygame.Rect(next_button_x, footer_button_y, footer_button_width, footer_button_height)
        
        # Cancel button
        cancel_button_x = footer_center - footer_button_width // 2
        self.navigation_buttons["cancel"] = pygame.Rect(cancel_button_x, footer_button_y, footer_button_width, footer_button_height)
        
        # Tab buttons - wider tabs for better visibility
        tab_width = 120
        tab_height = 40
        tab_spacing = (screen_width - margin*2 - tab_width*4) // 3  # Distribute tabs evenly
        tab_start_x = self.ui_regions["tabs"].x
        tab_y = self.ui_regions["tabs"].y + (self.ui_regions["tabs"].height - tab_height) // 2
        
        self.tab_buttons = [
            {
                "text": "Name",
                "value": "name",
                "rect": pygame.Rect(tab_start_x, tab_y, tab_width, tab_height)
            },
            {
                "text": "Appearance",
                "value": "appearance",
                "rect": pygame.Rect(tab_start_x + tab_width + tab_spacing, tab_y, tab_width, tab_height)
            },
            {
                "text": "Attributes",
                "value": "attributes",
                "rect": pygame.Rect(tab_start_x + (tab_width + tab_spacing) * 2, tab_y, tab_width, tab_height)
            },
            {
                "text": "Abilities",
                "value": "abilities",
                "rect": pygame.Rect(tab_start_x + (tab_width + tab_spacing) * 3, tab_y, tab_width, tab_height)
            },
            {
                "text": "Background",
                "value": "background",
                "rect": pygame.Rect(tab_start_x + (tab_width + tab_spacing) * 4, tab_y, tab_width, tab_height)
            }
        ]
        
        # Appearance options
        self.appearance_options = [
            {
                "text": "Gender", 
                "property": "gender", 
                "values": ["male", "female"], 
                "get": lambda: self.character_data["gender"], 
                "set": lambda val: self._set_character_property("gender", val)
            },
            {
                "text": "Skin Tone", 
                "property": "skin_tone", 
                "values": [0, 1, 2, 3], 
                "get": lambda: self.character_data["appearance"]["skin_tone"], 
                "set": lambda val: self._set_appearance_property("skin_tone", val)
            },
            {
                "text": "Hair Style", 
                "property": "hair_style", 
                "values": [0, 1, 2, 3, 4, 5], 
                "get": lambda: self.character_data["appearance"]["hair_style"], 
                "set": lambda val: self._set_appearance_property("hair_style", val)
            },
            {
                "text": "Hair Color", 
                "property": "hair_color", 
                "values": [0, 1, 2, 3, 4, 5], 
                "get": lambda: self.character_data["appearance"]["hair_color"], 
                "set": lambda val: self._set_appearance_property("hair_color", val)
            },
            {
                "text": "Face Style", 
                "property": "face_style", 
                "values": [0, 1, 2, 3], 
                "get": lambda: self.character_data["appearance"]["face_style"], 
                "set": lambda val: self._set_appearance_property("face_style", val)
            },
            {
                "text": "Body Type", 
                "property": "body_type", 
                "values": [0, 1, 2], 
                "get": lambda: self.character_data["appearance"]["body_type"], 
                "set": lambda v: self._set_appearance_property("body_type", v)
            }
        ]
         
        # Attribute options
        self.attribute_options = [
            {
                "name": "Strength", 
                "property": "strength", 
                "text": "Strength", 
                "property": "strength", 
                "description": "Physical power for melee attacks and carrying capacity.", 
                "min": 8, "max": 15,  # Changed max from 18 to 15
                "get": lambda: self.character_data["attributes"]["strength"], 
                "set": lambda v: self._set_attribute_property("strength", v)
            },
            {
                "text": "Dexterity", 
                "property": "dexterity", 
                "description": "Agility, reflexes, and precision for ranged attacks.", 
                "min": 8, "max": 15,  # Changed max from 18 to 15
                "get": lambda: self.character_data["attributes"]["dexterity"], 
                "set": lambda v: self._set_attribute_property("dexterity", v)
            },
            {
                "text": "Intelligence", 
                "property": "intelligence", 
                "description": "Mental acuity for spellcasting and solving puzzles.", 
                "min": 8, "max": 15,  # Changed max from 18 to 15
                "get": lambda: self.character_data["attributes"]["intelligence"], 
                "set": lambda v: self._set_attribute_property("intelligence", v)
            },
            {
                "text": "Vitality", 
                "property": "vitality", 
                "description": "Stamina and health, determines hit points.", 
                "min": 8, "max": 15,  # Changed max from 18 to 15
                "get": lambda: self.character_data["attributes"]["vitality"], 
                "set": lambda v: self._set_attribute_property("vitality", v)
            },
            {
                "text": "Charisma", 
                "property": "charisma", 
                "description": "Personality and persuasion ability for social interactions.", 
                "min": 8, "max": 15,  # Changed max from 18 to 15
                "get": lambda: self.character_data["attributes"]["charisma"], 
                "set": lambda v: self._set_attribute_property("charisma", v)
            }
        ]
         
        # Create ability options - these will be populated based on the selected class
        self.ability_options = []
        
    def _create_preview_character(self):
        """Create a preview character entity for visualization."""
        # Create preview entity
        preview_entity = self.world.create_entity()
        self.preview_entity_id = preview_entity.id
        
        # Set initial position (center of screen)
        position = np.array([self.renderer.width // 2, self.renderer.height // 2], dtype=float)
        
        # Add components
        preview_entity.add_component(Transform(position=position))
        preview_entity.add_component(Sprite(texture_path="assets/sprites/player.png"))
        
        # Add entity to scene's managed entities
        self.add_entity(self.preview_entity_id)
        
        # Initialize procedural generator for character appearance
        try:
            from tools.procedural.animation.character_generator import CharacterGenerator
            self.procedural_generator = CharacterGenerator()
            print("Procedural character generator initialized")
        except ImportError as e:
            print(f"Could not initialize procedural character generator: {e}")
            self.procedural_generator = None
        
    def _setup_class_selection(self):
        """Set up UI for class selection step."""
        self.current_step = "class"
        # Clear existing UI elements
        self.active_ui_elements = []
        
        # Create class selection buttons and descriptions
        # In a real implementation, these would be proper UI widgets
        
    def _setup_appearance_customization(self):
        """Set up UI for appearance customization step."""
        self.current_step = "appearance"
        # Clear existing UI elements
        self.active_ui_elements = []
        
        # Create appearance customization controls
        # Body type, face, hair style/color, outfit
        
    def _setup_attribute_distribution(self):
        """Set up UI for attribute distribution step."""
        self.current_step = "attributes"
        # Clear existing UI elements
        self.active_ui_elements = []
        
        # Create attribute distribution controls
        # Sliders or +/- buttons for each attribute
        
    def _setup_background_selection(self):
        """Set up UI for background selection step."""
        self.current_step = "background"
        # Clear existing UI elements
        self.active_ui_elements = []
        
        # Create background selection buttons and descriptions
        
    def _setup_name_selection(self):
        """Set up UI for name selection step."""
        self.current_step = "name"
        # Clear existing UI elements
        self.active_ui_elements = []
        
        # Create input field state
        self.name_input_active = True
        self.name_input_cursor_visible = True
        self.name_input_cursor_timer = 0
        self.name_input_cursor_blink_rate = 0.5  # Blink every 0.5 seconds
        
        # Set up name options
        self.random_names = {
            "male": [
                "Alaric", "Bran", "Cedric", "Darius", "Eadric", 
                "Finnian", "Gawain", "Hadrian", "Ivan", "Jorah",
                "Kael", "Leif", "Magnus", "Nolan", "Orin",
                "Percy", "Quentin", "Rowan", "Seth", "Taran"
            ],
            "female": [
                "Astrid", "Briar", "Celia", "Daria", "Elara",
                "Freya", "Giselle", "Helena", "Isolde", "Juno",
                "Kira", "Lyra", "Maren", "Nadia", "Ophelia",
                "Phoebe", "Quinn", "Rhiannon", "Selene", "Thea"
            ]
        }
        
    def _setup_equipment_selection(self):
        """Set up UI for starting equipment selection step."""
        self.current_step = "equipment"
        # Clear existing UI elements
        self.active_ui_elements = []
        
        # Create equipment selection based on class and background
        
    def _setup_summary(self):
        """Set up UI for character summary and confirmation step."""
        self.current_step = "summary"
        # Clear existing UI elements
        self.active_ui_elements = []
        
        # Create summary display and confirmation button
        
    def update(self, dt):
        """
        Update scene logic for the current frame.
        
        Args:
            dt (float): Time elapsed since last frame.
        """
        # Update preview character based on current selections
        self._update_preview_character()
        
        # Update UI elements
        self._update_ui(dt)
        
        # Update name input cursor blinking
        if self.current_step == "name":
            self.name_input_cursor_timer += dt
            if self.name_input_cursor_timer >= self.name_input_cursor_blink_rate:
                self.name_input_cursor_timer = 0
                self.name_input_cursor_visible = not self.name_input_cursor_visible
        
    def _update_preview_character(self):
        """Update preview character based on current selections."""
        # Get preview entity
        preview_entity = self.world.get_entity(self.preview_entity_id)
        if not preview_entity:
            return
            
        # Update sprite based on class, body type, etc.
        sprite = preview_entity.get_component(Sprite)
        if sprite and self.character_data["class"]:
            # Update sprite texture path based on selections
            class_id = self.character_data["class"]["id"]
            body_type = self.character_data["appearance"]["body_type"]
            # In a real implementation, this would construct the path to the correct sprite
            # sprite.texture_path = f"assets/sprites/characters/{class_id}_{body_type}.png"
            
    def _update_ui(self, dt):
        """Update UI elements."""
        # Update any animated UI elements
        pass
        
    def render(self, screen=None):
        """
        Render the character creation scene.
        
        Args:
            screen: The pygame screen surface to render on.
                   If None, use the renderer's screen.
        """
        # Use the renderer's screen if screen is not provided
        if screen is None:
            screen = self.renderer.screen
        
        try:
            # Clear screen with a basic background color
            screen.fill((20, 20, 40))  # Dark blue background
            
            # If OpenGL is available, try to use the OpenGL renderer
            if self.using_opengl and self.ui_renderer is not None:
                try:
                    # Render background
                    self._render_background(screen)
                    
                    # Render UI elements
                    self._render_ui_frame(screen)
                    
                    # Render current step UI
                    self._render_step_ui(screen)
                    
                    # Render character preview only on the appearance tab or when showing tabs
                    if self.current_step in ["appearance", "summary"]:
                        self._render_preview_character(screen)
                    
                    # Render navigation buttons
                    self._render_navigation_buttons(screen)
                    
                except Exception as e:
                    # If OpenGL rendering fails, log the error and fall back to PyGame
                    print(f"Error in OpenGL rendering: {e}")
                    import traceback
                    traceback.print_exc()
                    self.using_opengl = False
                    
                    # Fallback to PyGame rendering
                    self.render(screen)
            else:
                # PyGame rendering as fallback
                # Clear screen
                screen.fill((20, 20, 40))  # Dark blue background
                
                # Render background
                self._render_background(screen)
                
                # Render UI elements
                self._render_ui_frame(screen)
                
                # Render current step UI
                self._render_step_ui(screen)
                
                # Render character preview only on the appearance tab
                if self.current_step in ["appearance", "summary"]:
                    self._render_preview_character(screen)
                
                # Render navigation buttons
                self._render_navigation_buttons(screen)
        
        except Exception as e:
            # Handle any rendering errors gracefully
            print(f"Error rendering character creation scene: {e}")
            import traceback
            traceback.print_exc()
            
            # Render a simple error message
            error_font = pygame.font.SysFont(None, 36)
            error_text = error_font.render("Error rendering character creation scene", True, (255, 100, 100))
            screen.blit(error_text, (100, 100))
        
    def _render_background(self, screen):
        """Render scene background with a more atmospheric gradient effect."""
        if self.using_opengl:
            # Use OpenGL renderer to draw a background
            width = self.renderer.width
            height = self.renderer.height
            
            # Get class-specific colors if a class is selected
            top_color = (0.1, 0.12, 0.2, 1.0)  # Default dark blue
            bottom_color = (0.05, 0.05, 0.1, 1.0)  # Default very dark blue
            
            for cls in self.available_classes:
                if cls["id"] == self.character_data["class"]:
                    # Use class colors with reduced intensity for background
                    main_color = cls["visuals"].main_color
                    accent_color = cls["visuals"].accent_color
                    
                    # Create gradient from accent to main color, darkened
                    top_r = max(0.05, accent_color[0] * 0.3)
                    top_g = max(0.05, accent_color[1] * 0.3)
                    top_b = max(0.05, accent_color[2] * 0.3)
                    
                    bottom_r = max(0.02, main_color[0] * 0.15)
                    bottom_g = max(0.02, main_color[1] * 0.15)
                    bottom_b = max(0.02, main_color[2] * 0.15)
                    
                    top_color = (top_r, top_g, top_b, 1.0)
                    bottom_color = (bottom_r, bottom_g, bottom_b, 1.0)
                    break
            
            # Convert to RGB 0-255 range for OpenGL renderer
            top_color_rgb = (int(top_color[0] * 255), int(top_color[1] * 255), 
                            int(top_color[2] * 255), int(top_color[3] * 255))
            bottom_color_rgb = (int(bottom_color[0] * 255), int(bottom_color[1] * 255), 
                               int(bottom_color[2] * 255), int(bottom_color[3] * 255))
            
            # Instead of a gradient (not available), use the top color for full background
            self.ui_renderer.draw_rectangle(
                0, 0, width, height,
                top_color_rgb
            )
            
            # Add some panels with different colors to simulate a gradient effect
            panel_height = height // 4
            for i in range(4):
                # Calculate an interpolated color between top and bottom
                t = (i + 1) / 4.0  # interpolation factor
                r = int(top_color_rgb[0] * (1 - t) + bottom_color_rgb[0] * t)
                g = int(top_color_rgb[1] * (1 - t) + bottom_color_rgb[1] * t)
                b = int(top_color_rgb[2] * (1 - t) + bottom_color_rgb[2] * t)
                a = int(top_color_rgb[3] * (1 - t) + bottom_color_rgb[3] * t)
                
                color = (r, g, b, a)
                self.ui_renderer.draw_rectangle(
                    0, 
                    i * panel_height, 
                    width, 
                    panel_height,
                    color
                )
            
            # Add a semi-transparent overlay at the top (for title area)
            self.ui_renderer.draw_rectangle(
                0, 0, width, self.ui_regions["header"].height,
                (0, 0, 0, 128)
            )
            
            # Draw a semi-transparent overlay for the tabs area
            self.ui_renderer.draw_rectangle(
                0, self.ui_regions["tabs"].y, 
                width, self.ui_regions["tabs"].height,
                (0, 0, 0, 77)
            )
            
            # Draw a semi-transparent overlay for the main content area
            content_x = self.ui_regions["content"].x
            content_y = self.ui_regions["content"].y
            content_width = self.ui_regions["content"].width
            content_height = self.ui_regions["content"].height
            
            self.ui_renderer.draw_rectangle(
                content_x, content_y, 
                content_width, content_height,
                (0, 0, 0, 179)
            )
            
            # Draw a darker panel for the character preview
            preview_x = self.ui_regions["preview"].x
            preview_y = self.ui_regions["preview"].y
            preview_width = self.ui_regions["preview"].width
            preview_height = self.ui_regions["preview"].height
            
            self.ui_renderer.draw_rectangle(
                preview_x, preview_y,
                preview_width, preview_height,
                (0, 0, 0, 204)
            )
            
            # Draw footer area for navigation buttons
            self.ui_renderer.draw_rectangle(
                0, self.ui_regions["navigation"].y,
                width, self.ui_regions["navigation"].height,
                (0, 0, 0, 153)
            )
            
            # Add some decorative elements based on the selected class
            if self.character_data["class"]:
                for cls in self.available_classes:
                    if cls["id"] == self.character_data["class"]:
                        # Add some subtle decorative elements in the corners using class colors
                        accent_color = cls["visuals"].accent_color
                        accent_alpha = 0.3
                        
                        # Convert to RGB 0-255 range
                        accent_color_rgb = (
                            int(accent_color[0] * 255), 
                            int(accent_color[1] * 255), 
                            int(accent_color[2] * 255), 
                            int(accent_alpha * 255)
                        )
                        
                        # Top-left corner decoration
                        self.ui_renderer.draw_rectangle(
                            0, 0, 100, 5,
                            accent_color_rgb
                        )
                        self.ui_renderer.draw_rectangle(
                            0, 0, 5, 100,
                            accent_color_rgb
                        )
                        
                        # Bottom-right corner decoration
                        self.ui_renderer.draw_rectangle(
                            width - 100, height - 5, 100, 5,
                            accent_color_rgb
                        )
                        self.ui_renderer.draw_rectangle(
                            width - 5, height - 100, 5, 100,
                            accent_color_rgb
                        )
                        break
        else:
            # PyGame fallback rendering
            screen.fill((20, 20, 40))  # Dark blue background
        
    def _render_preview_character(self, screen):
        """Render preview character."""
        preview_x = self.renderer.width // 2 - 50
        preview_y = self.renderer.height // 2 - 50
        
        if self.using_opengl:
            # For OpenGL, we can draw simple shapes to represent the character
            # Head (circle approximated by a rectangle with opacity)
            self.ui_renderer.draw_rectangle(
                preview_x + 25, preview_y, 50, 50, 
                (255, 200, 150, 255)  # Skin tone
            )
            
            # Body (rectangle)
            self.ui_renderer.draw_rectangle(
                preview_x + 10, preview_y + 50, 
                80, 100, (100, 100, 150, 255)  # Body color
            )
            
            # If we had a proper texture, we would use:
            # self.ui_renderer.draw_texture(texture_id, preview_x, preview_y, width, height)
        else:
            # With PyGame we can use drawing primitives directly
        # Normally, the world renderer would handle this
        # For now, just draw a simple placeholder
            pygame.draw.circle(screen, (255, 200, 150), 
                          (screen.get_width() // 2, screen.get_height() // 2), 
                          50)  # Head
            pygame.draw.rect(screen, (100, 100, 150), 
                         (screen.get_width() // 2 - 40, 
                          screen.get_height() // 2 + 50, 
                          80, 100))  # Body
        
    def _render_ui_frame(self, screen):
        """Render the main UI frame including title and tabs."""
        # Get current mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        if self.using_opengl:
            # Render title
            title_text = f"Character Creation - {self._get_step_title()}"
            self.ui_renderer.render_text(
                title_text,
                self.title_font,
                (255, 255, 255, 255),
                40, 20
            )
            
            # Render step subtitle with instructions
            subtitle = self._get_step_instructions()
            self.ui_renderer.render_text(
                subtitle,
                self.small_font,
                (200, 200, 200, 200),
                40, 55
            )
            
            # Render tabs if we're not in the class selection step
            if self.current_step != "class":
                # Variable to track if we're hovering over any tab to show tooltip
                hovered_tab = None
                
                for tab in self.tab_buttons:
                    # Determine if this tab is active or being hovered over
                    is_active = tab["value"] == self.active_tab
                    is_hovered = tab["rect"].collidepoint(mouse_pos)
                    
                    # Store hovered tab for tooltip
                    if is_hovered:
                        hovered_tab = tab
                    
                    # Choose colors based on active and hover state
                    tab_color = (60, 80, 120, 255) if is_active else (50, 50, 70, 200)
                    text_color = (255, 255, 255, 255) if is_active else (200, 200, 220, 200)
                    
                    # Draw tab background
                    self.ui_renderer.draw_rectangle(
                        tab["rect"].x, tab["rect"].y,
                        tab["rect"].width, tab["rect"].height,
                        tab_color
                    )
                    
                    # Draw tab text
                    self.ui_renderer.render_text(
                        tab["text"],
                        self.text_font,
                        text_color,
                        tab["rect"].x + 15, tab["rect"].y + 10
                    )
                    
                    # Add a bright highlight bar under the active tab
                    if is_active:
                        highlight_height = 3
                        self.ui_renderer.draw_rectangle(
                            tab["rect"].x, tab["rect"].y + tab["rect"].height - highlight_height,
                            tab["rect"].width, highlight_height,
                            (100, 180, 255, 255)
                    )
        else:
            # PyGame fallback rendering with the same hover functionality
            # Render title
            title_text = f"Character Creation - {self._get_step_title()}"
            title_surface = self.title_font.render(title_text, True, (255, 255, 255))
            screen.blit(title_surface, (40, 20))
            
            # Render step subtitle
            subtitle = self._get_step_instructions()
            subtitle_surface = self.small_font.render(subtitle, True, (200, 200, 200))
            screen.blit(subtitle_surface, (40, 55))
            
            # Render tabs if we're not in the class selection step
            if self.current_step != "class":
                # Variable to track if we're hovering over any tab to show tooltip
                hovered_tab = None
                
                for tab in self.tab_buttons:
                    # Determine if this tab is active or being hovered over
                    is_active = tab["value"] == self.active_tab
                    is_hovered = tab["rect"].collidepoint(mouse_pos)
                    
                    # Store hovered tab for tooltip
                    if is_hovered:
                        hovered_tab = tab
                    
                    # Choose colors based on active and hover state
                    if is_active:
                        bg_color = (70, 90, 130)  # Brighter blue for active
                        text_color = (255, 255, 255)
                        border_color = (120, 180, 255)
                    elif is_hovered:
                        bg_color = (60, 80, 120)  # Slightly highlighted when hovered
                        text_color = (230, 230, 250)
                        border_color = (100, 140, 200)
                    else:
                        bg_color = (40, 40, 60)  # Dark when inactive
                        text_color = (180, 180, 200)
                        border_color = (80, 100, 140)
                    
                    # Draw tab background
                    pygame.draw.rect(screen, bg_color, tab["rect"])
                    
                    # Draw tab border
                    pygame.draw.rect(screen, border_color, tab["rect"], 2)
                    
                    # Draw tab text
                    text_surface = self.text_font.render(tab["text"], True, text_color)
                    text_rect = text_surface.get_rect(center=(
                        tab["rect"].x + tab["rect"].width // 2,
                        tab["rect"].y + tab["rect"].height // 2
                    ))
                    screen.blit(text_surface, text_rect)
                
                # Draw tooltip for hovered tab
                if hovered_tab and "tooltip" in hovered_tab:
                    tooltip_x = mouse_pos[0] + 15  # Offset from cursor
                    tooltip_y = mouse_pos[1] + 15
                    tooltip_text = hovered_tab["tooltip"]
                    
                    # Create tooltip surface with semi-transparent background
                    tooltip_font = self.small_font
                    tooltip_surface = tooltip_font.render(tooltip_text, True, (220, 220, 255))
                    tooltip_width = tooltip_surface.get_width() + 10
                    tooltip_height = tooltip_surface.get_height() + 10
                    
                    # Create background surface with transparency
                    tooltip_bg = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
                    tooltip_bg.fill((40, 40, 60, 230))
                    
                    # Draw border
                    pygame.draw.rect(tooltip_bg, (100, 140, 200, 200), 
                                    pygame.Rect(0, 0, tooltip_width, tooltip_height), 1)
                    
                    # Blit text onto background
                    tooltip_bg.blit(tooltip_surface, (5, 5))
                    
                    # Draw the tooltip
                    screen.blit(tooltip_bg, (tooltip_x, tooltip_y))
        
    def _render_step_ui(self, screen):
        """Render the UI for the current step."""
        # Get content area position and dimensions
        content_rect = self.ui_regions["main_content"]
        content_x = content_rect.x + 20
        content_y = content_rect.y + 20
        
        print(f"Rendering step UI for current_step: {self.current_step}, active_tab: {self.active_tab}")
        
        # Render UI based on current step
        if self.current_step == "class":
            self._render_class_options(screen)
        elif self.current_step == "appearance":
            self._render_appearance_tab(screen, content_x, content_y)
        elif self.current_step == "attributes":
            self._render_attributes_tab(screen, content_x, content_y)
        elif self.current_step == "background":
            self._render_background_tab(screen, content_x, content_y)
        elif self.current_step == "abilities":
            self._render_abilities_tab(screen, content_x, content_y)
        elif self.current_step == "name":
            self._render_name_tab(screen, content_x, content_y)
        elif self.current_step == "equipment":
            # Future: Render equipment selection
            pass
        elif self.current_step == "summary":
            # Future: Render character summary and confirmation
            pass
        
    def _render_abilities_tab(self, screen, content_x, content_y):
        """Render the abilities tab content with class abilities."""
        if self.using_opengl:
            # Get main content dimensions
            content_width = self.ui_regions["main_content"].width
            content_height = self.ui_regions["main_content"].height
            
            # Apply scroll offset
            adjusted_y = content_y - self.scroll_offset
            
            # Instructions at the top
            instruction_text = "These are the unique abilities for your selected class"
            self.ui_renderer.render_text(
                instruction_text,
                self.small_font,
                (200, 200, 220, 220),
                content_x + content_width // 2 - len(instruction_text) * 3, adjusted_y
            )
            
            # Display character summary section
            self._render_character_summary(content_x, adjusted_y + 30, content_width)
            
            # No abilities message if none available
            if not self.ability_options:
                if self.character_data["class"] is None:
                    # No class selected
                    no_class_text = "Select a character class to view available abilities."
                    self.ui_renderer.render_text(
                        no_class_text,
                        self.text_font,
                        (200, 150, 150, 255),
                        content_x + content_width // 2 - len(no_class_text) * 3, adjusted_y + 150
                    )
                else:
                    # Class selected but no abilities (this should not happen)
                    no_abilities_text = "No abilities available for this class."
                    self.ui_renderer.render_text(
                        no_abilities_text,
                        self.text_font,
                        (200, 150, 150, 255),
                        content_x + content_width // 2 - len(no_abilities_text) * 3, adjusted_y + 150
                    )
            return
            
            # Draw abilities list
            y_pos = adjusted_y + 140
            ability_height = 80
            ability_spacing = 15
            ability_width = content_width - 40
            
            # Note text
            note_text = "Note: These abilities are automatically granted to your character when you start the game."
            self.ui_renderer.render_text(
                note_text,
                self.small_font,
                (180, 180, 200, 200),
                content_x, y_pos - 30
            )
            
            for i, ability in enumerate(self.ability_options):
                # Calculate position with scrolling
                ability_y = y_pos + i * (ability_height + ability_spacing)
                
                # Skip if outside visible area
                if (ability_y + ability_height < self.ui_regions["content"].y or
                    ability_y > self.ui_regions["content"].y + self.ui_regions["content"].height):
                    continue
                
                # Background color based on ability type
                bg_color = (40, 40, 60, 150)  # Default dark blue
                if "type" in ability:
                    if ability["type"] == AbilityType.PHYSICAL:
                        bg_color = (60, 40, 40, 150)  # Reddish for physical
                    elif ability["type"] == AbilityType.MAGICAL:
                        bg_color = (40, 40, 80, 150)  # Blue for magical
                    elif ability["type"] == AbilityType.HYBRID:
                        bg_color = (60, 40, 80, 150)  # Purple for hybrid
                    elif ability["type"] == AbilityType.BUFF:
                        bg_color = (40, 60, 40, 150)  # Green for buffs
                    elif ability["type"] == AbilityType.DEBUFF:
                        bg_color = (60, 40, 60, 150)  # Purple for debuffs
                
                # Draw ability card background
                self.ui_renderer.draw_rectangle(
                    content_x, ability_y,
                    ability_width, ability_height,
                    bg_color
                )
                
                # Draw ability name
                self.ui_renderer.render_text(
                    ability["name"],
                    self.text_font,
                    (255, 255, 255, 255),
                    content_x + 15, ability_y + 15
                )
                
                # Draw ability description
                if "description" in ability:
                    # For multi-line descriptions, wrap the text
                    description_lines = self._wrap_text(
                        ability["description"],
                        self.small_font,
                        ability_width - 30
                    )
                    
                    for j, line in enumerate(description_lines):
                        self.ui_renderer.render_text(
                            line,
                            self.small_font,
                            (200, 200, 220, 200),
                            content_x + 20, ability_y + 45 + j * 20
                        )
            
            # Update max scroll value
            last_ability_y = y_pos + len(self.ability_options) * (ability_height + ability_spacing)
            self.max_scroll = max(0, last_ability_y - content_height)
        else:
            # Pygame fallback implementation
            pass
            
    def _render_class_options(self, screen):
        """Render class selection options with a visually appealing card-based layout."""
        if self.using_opengl:
            # Title for the section
            self.ui_renderer.render_text(
                "Choose Your Class",
                self.heading_font,
                (230, 230, 255, 255),
                self.ui_regions["content"].x, self.ui_regions["content"].y
            )
            
            # Calculate layout for class cards
            card_width = 270
            card_height = 240  # Increased height for more details and abilities
            cards_per_row = 2
            card_margin = 20
            start_x = self.ui_regions["content"].x + 10
            start_y = self.ui_regions["content"].y + 60
            
            # Instruction text
            instruction_text = "Select a class to view detailed information. Each class has unique abilities and strengths."
            self.ui_renderer.render_text(
                instruction_text,
                self.small_font,
                (200, 200, 200, 200),
                self.ui_regions["content"].x, self.ui_regions["content"].y + 30
            )
            
            # Get current mouse position for hover effects
            mouse_pos = pygame.mouse.get_pos()
            
            # Render each class as a selectable card
            for i, cls in enumerate(self.available_classes):
                # Calculate position
                row = i // cards_per_row
                col = i % cards_per_row
                
                card_x = start_x + col * (card_width + card_margin)
                card_y = start_y + row * (card_height + card_margin)
                
                # Determine if this class is selected or hovered
                is_selected = False
                if self.character_data["class"]:
                    if isinstance(self.character_data["class"], dict) and "id" in self.character_data["class"]:
                        is_selected = cls["id"] == self.character_data["class"]["id"]
                    else:
                        is_selected = cls["id"] == self.character_data["class"]
                
                is_hovered = pygame.Rect(card_x, card_y, card_width, card_height).collidepoint(mouse_pos)
                
                # Get class colors for styling
                main_color = cls["visuals"].main_color
                accent_color = cls["visuals"].accent_color
                
                # Calculate colors for card elements
                if is_selected:
                    # Selected class gets brighter colors
                    bg_color = (
                        int(min(1.0, main_color[0] * 0.3 + 0.1) * 255),
                        int(min(1.0, main_color[1] * 0.3 + 0.1) * 255),
                        int(min(1.0, main_color[2] * 0.3 + 0.1) * 255),
                        230
                    )
                    border_color = (
                        int(accent_color[0] * 255),
                        int(accent_color[1] * 255),
                        int(accent_color[2] * 255),
                        255
                    )
                    title_color = (
                        int(min(1.0, accent_color[0] + 0.3) * 255),
                        int(min(1.0, accent_color[1] + 0.3) * 255),
                        int(min(1.0, accent_color[2] + 0.3) * 255),
                        255
                    )
                    text_color = (220, 220, 220, 255)
                elif is_hovered:
                    # Hovered class gets slightly brighter colors
                    bg_color = (
                        int(min(1.0, main_color[0] * 0.25 + 0.05) * 255),
                        int(min(1.0, main_color[1] * 0.25 + 0.05) * 255),
                        int(min(1.0, main_color[2] * 0.25 + 0.05) * 255),
                        220
                    )
                    border_color = (
                        int(accent_color[0] * 0.9 * 255),
                        int(accent_color[1] * 0.9 * 255),
                        int(accent_color[2] * 0.9 * 255),
                        220
                    )
                    title_color = (
                        int(min(1.0, accent_color[0] * 0.9 + 0.2) * 255),
                        int(min(1.0, accent_color[1] * 0.9 + 0.2) * 255),
                        int(min(1.0, accent_color[2] * 0.9 + 0.2) * 255),
                        240
                    )
                    text_color = (200, 200, 200, 240)
                else:
                    # Unselected classes get darker colors
                    bg_color = (30, 30, 40, 204)
                    border_color = (
                        int(main_color[0] * 0.7 * 255),
                        int(main_color[1] * 0.7 * 255),
                        int(main_color[2] * 0.7 * 255),
                        179
                    )
                    title_color = (
                        int(min(1.0, accent_color[0] * 0.8 + 0.2) * 255),
                        int(min(1.0, accent_color[1] * 0.8 + 0.2) * 255),
                        int(min(1.0, accent_color[2] * 0.8 + 0.2) * 255),
                        230
                    )
                    text_color = (180, 180, 180, 200)
                
                # Store card rect for click detection
                cls["rect"] = pygame.Rect(card_x, card_y, card_width, card_height)
                
                # Draw card background
                self.ui_renderer.draw_rectangle(
                    card_x, card_y, card_width, card_height,
                    bg_color
                )
                
                # Draw card border 
                border_thickness = 2
                # Top border
                self.ui_renderer.draw_rectangle(
                    card_x, card_y,
                    card_width, border_thickness,
                    border_color
                )
                # Bottom border
                self.ui_renderer.draw_rectangle(
                    card_x, card_y + card_height - border_thickness,
                    card_width, border_thickness,
                    border_color
                )
                # Left border
                self.ui_renderer.draw_rectangle(
                    card_x, card_y,
                    border_thickness, card_height,
                    border_color
                )
                # Right border
                self.ui_renderer.draw_rectangle(
                    card_x + card_width - border_thickness, card_y,
                    border_thickness, card_height,
                    border_color
                )
                
                # Draw class name with a highlight/glow effect if selected
                if is_selected or is_hovered:
                    # Draw a subtle glow behind the text for selected/hovered items
                    glow_color = (
                        int(accent_color[0] * 0.5 * 255),
                        int(accent_color[1] * 0.5 * 255),
                        int(accent_color[2] * 0.5 * 255),
                        120
                    )
                    self.ui_renderer.draw_rectangle(
                        card_x + 10, card_y + 10,
                        len(cls["name"].upper()) * 14, 30,
                        glow_color
                )
                
                # Draw class name
                self.ui_renderer.render_text(
                    cls["name"].upper(),
                    self.text_font,
                    title_color,
                    card_x + 15, card_y + 15
                )
                
                # Draw class description (shortened for space)
                description_lines = self._wrap_text(
                    cls["description"].split('\n')[0],  # Only the first paragraph
                    self.small_font, 
                    card_width - 30
                )
                
                for j, line in enumerate(description_lines):
                    if j < 3:  # Limit to first 3 lines for space
                        self.ui_renderer.render_text(
                        line,
                        self.small_font,
                        text_color,
                        card_x + 15, card_y + 50 + j * 20
                    )
                
                # Draw class stats as small bars
                stat_x = card_x + 15
                stat_y = card_y + 110
                stat_width = 80
                stat_height = 6
                stat_spacing = 16
                
                # Define stats to display
                stats = [
                    ("STR", cls["stats"].strength, (204, 51, 51, 204)),
                    ("INT", cls["stats"].intelligence, (51, 153, 204, 204)),
                    ("AGI", cls["stats"].agility, (51, 204, 51, 204)),
                    ("DEF", cls["stats"].defense, (204, 204, 51, 204))
                ]
                
                # Draw stat bars
                for j, (stat_name, stat_value, stat_color) in enumerate(stats):
                    # Draw stat name
                    if j < 2:
                        # First row
                        pos_x = stat_x + j * (stat_width + 20)
                        pos_y = stat_y
                    else:
                        # Second row
                        pos_x = stat_x + (j - 2) * (stat_width + 20)
                        pos_y = stat_y + stat_spacing
                    
                    # Draw stat label
                    self.ui_renderer.render_text(
                        stat_name,
                        self.small_font,
                        text_color,
                        pos_x, pos_y
                    )
                    
                    # Draw stat bar background
                    self.ui_renderer.draw_rectangle(
                        pos_x + 30, pos_y + 6,
                        stat_width, stat_height,
                        (80, 80, 80, 150)
                    )
                    
                    # Calculate fill amount (normalize between 0-18)
                    fill_amount = min(1.0, stat_value / 18.0)
                    
                    # Draw stat bar fill
                    self.ui_renderer.draw_rectangle(
                        pos_x + 30, pos_y + 6,
                        int(stat_width * fill_amount), stat_height,
                        stat_color
                    )
                
                    # Display abilities section label
                    self.ui_renderer.render_text(
                    "Key Abilities:",
                    self.small_font,
                    (200, 200, 255, 220),
                    card_x + 15, card_y + 155
                    )
                
                # Display abilities for this class
                try:
                    # Create a character instance to get abilities
                    char_instance = Character(cls["enum"])
                    
                    # Show top 2 abilities
                    ability_keys = list(char_instance.abilities.keys())
                    for j, ability_key in enumerate(ability_keys[:2]):
                        ability = char_instance.abilities[ability_key]
                        ability_y = card_y + 175 + j * 20
                        
                        # Draw ability name and type
                        ability_text = f"• {ability.name}"
                        ability_color = (220, 220, 255, 220)
                        
                        # Color-code ability by type
                        if ability.type == AbilityType.PHYSICAL:
                            ability_color = (220, 150, 150, 220)
                        elif ability.type == AbilityType.MAGICAL:
                            ability_color = (150, 150, 220, 220)
                        elif ability.type == AbilityType.BUFF:
                            ability_color = (150, 220, 150, 220)
                        elif ability.type == AbilityType.SUMMON:
                            ability_color = (220, 180, 150, 220)
                        
                        self.ui_renderer.render_text(
                            ability_text,
                            self.small_font,
                            ability_color,
                            card_x + 20, ability_y
                        )
                except Exception as e:
                    # Fallback if abilities can't be loaded
                    self.ui_renderer.render_text(
                        "Abilities info unavailable",
                        self.small_font,
                        (200, 150, 150, 220),
                        card_x + 20, card_y + 175
                    )
                
                # Add specialty information for each class
                specialty_text = "Specialty: " + ", ".join(cls.get("specialties", ["Unknown"])[:2])
                
                self.ui_renderer.render_text(
                    specialty_text,
                    self.small_font,
                    (200, 200, 255, 220),
                    card_x + 15, card_y + 215
                )
                
                # Add a difficulty rating for each class
                difficulty = cls.get("difficulty", 2)
                difficulty_text = "Difficulty: " + "★" * difficulty + "☆" * (3 - difficulty)
                
                self.ui_renderer.render_text(
                    difficulty_text,
                    self.small_font,
                    (220, 220, 150, 220),
                    card_x + 15, card_y + 235
                )
                
                # Add a selection indicator if this class is selected
                if is_selected:
                    self.ui_renderer.draw_rectangle(
                        card_x + card_width - 30, card_y + 15,
                        15, 15,
                        border_color
            )
            
        else:
            # PyGame fallback rendering
            # Title for the section
            title_surface = self.heading_font.render("Choose Your Class", True, (230, 230, 255))
            screen.blit(title_surface, (self.ui_regions["content"].x, self.ui_regions["content"].y))
            
            # For simple PyGame fallback, we will implement a basic version
            # The full implementation would mirror the OpenGL version
        
    def _render_navigation_buttons(self, screen):
        """Render navigation buttons (previous, next, cancel, confirm) with improved visibility."""
        nav_region = self.ui_regions["navigation"]
        button_width = 150
        button_height = 40
        button_spacing = 20
        
        if self.using_opengl:
            # Previous button
            prev_button_x = nav_region.x + 50
            prev_button_y = nav_region.y + (nav_region.height - button_height) // 2
            
            # Create previous button rect for click detection
            prev_button_rect = pygame.Rect(prev_button_x, prev_button_y, button_width, button_height)
            
            # Determine if previous button should be enabled based on current step
            prev_enabled = self.current_step != "class"
            
            # Store button rect for click detection
            self.navigation_buttons["prev"] = prev_button_rect if prev_enabled else None
            
            if prev_enabled:
                # Draw button background with standard rectangle
                self.ui_renderer.draw_rectangle(
                    prev_button_x, prev_button_y, button_width, button_height,
                    (60, 80, 120, 200)
                )
                
                # Draw button border using 4 rectangles
                border_color = (100, 140, 200, 200)
                border_thickness = 2
                
                # Top border
                self.ui_renderer.draw_rectangle(
                    prev_button_x, prev_button_y,
                    button_width, border_thickness,
                    border_color
                )
                # Bottom border
                self.ui_renderer.draw_rectangle(
                    prev_button_x, prev_button_y + button_height - border_thickness,
                    button_width, border_thickness,
                    border_color
                )
                # Left border
                self.ui_renderer.draw_rectangle(
                    prev_button_x, prev_button_y,
                    border_thickness, button_height,
                    border_color
                )
                # Right border
                self.ui_renderer.draw_rectangle(
                    prev_button_x + button_width - border_thickness, prev_button_y,
                    border_thickness, button_height,
                    border_color
                )
                
                # Draw button text
                self.ui_renderer.render_text(
                    "< Previous",
                    self.text_font,
                    (220, 220, 255, 255),
                    prev_button_x + button_width // 2 - 40, prev_button_y + button_height // 2 - 8
                )
            
            # Next/Confirm button
            next_button_x = nav_region.x + nav_region.width - 50 - button_width
            next_button_y = nav_region.y + (nav_region.height - button_height) // 2
            
            # Create next button rect for click detection
            next_button_rect = pygame.Rect(next_button_x, next_button_y, button_width, button_height)
            
            # Determine button text based on current step
            if self.current_step == "summary":
                next_text = "Confirm"
                next_color = (80, 180, 80, 200)  # Green for confirm
                border_color = (120, 220, 120, 200)
            else:
                next_text = "Next >"
                next_color = (60, 80, 120, 200)  # Blue for next
                border_color = (100, 140, 200, 200)
            
            # Store button rect for click detection
            self.navigation_buttons["next"] = next_button_rect
            
            # Draw button background with standard rectangle
            self.ui_renderer.draw_rectangle(
                next_button_x, next_button_y, button_width, button_height,
                next_color
            )
            
            # Draw button border using 4 rectangles
            border_thickness = 2
            
            # Top border
            self.ui_renderer.draw_rectangle(
                next_button_x, next_button_y,
                button_width, border_thickness,
                border_color
            )
            # Bottom border
            self.ui_renderer.draw_rectangle(
                next_button_x, next_button_y + button_height - border_thickness,
                button_width, border_thickness,
                border_color
            )
            # Left border
            self.ui_renderer.draw_rectangle(
                next_button_x, next_button_y,
                border_thickness, button_height,
                border_color
            )
            # Right border
            self.ui_renderer.draw_rectangle(
                next_button_x + button_width - border_thickness, next_button_y,
                border_thickness, button_height,
                border_color
            )
            
            # Draw button text
            self.ui_renderer.render_text(
                next_text,
                self.text_font,
                (220, 220, 255, 255),
                next_button_x + button_width // 2 - 25, next_button_y + button_height // 2 - 8
            )
            
            # Cancel button (smaller and less prominent)
            cancel_button_width = 100
            cancel_button_x = nav_region.x + nav_region.width // 2 - cancel_button_width // 2
            cancel_button_y = nav_region.y + (nav_region.height - button_height) // 2
            
            # Create cancel button rect for click detection
            cancel_button_rect = pygame.Rect(cancel_button_x, cancel_button_y, cancel_button_width, button_height)
            
            # Store button rect for click detection
            self.navigation_buttons["cancel"] = cancel_button_rect
            
            # Draw button background with standard rectangle
            self.ui_renderer.draw_rectangle(
                cancel_button_x, cancel_button_y, cancel_button_width, button_height,
                (100, 60, 60, 180)
            )
            
            # Draw button border using 4 rectangles
            border_color = (150, 80, 80, 180)
            
            # Top border
            self.ui_renderer.draw_rectangle(
                cancel_button_x, cancel_button_y,
                cancel_button_width, border_thickness,
                border_color
            )
            # Bottom border
            self.ui_renderer.draw_rectangle(
                cancel_button_x, cancel_button_y + button_height - border_thickness,
                cancel_button_width, border_thickness,
                border_color
            )
            # Left border
            self.ui_renderer.draw_rectangle(
                cancel_button_x, cancel_button_y,
                border_thickness, button_height,
                border_color
            )
            # Right border
            self.ui_renderer.draw_rectangle(
                cancel_button_x + cancel_button_width - border_thickness, cancel_button_y,
                border_thickness, button_height,
                border_color
            )
            
            # Draw button text
            self.ui_renderer.render_text(
                "Cancel",
                self.text_font,
                (220, 200, 200, 255),
                cancel_button_x + cancel_button_width // 2 - 25, cancel_button_y + button_height // 2 - 8
            )
            
        else:
            # PyGame fallback rendering
            # Previous button
            prev_button_x = nav_region.x + 50
            prev_button_y = nav_region.y + (nav_region.height - button_height) // 2
            
            # Create previous button rect for click detection
            prev_button_rect = pygame.Rect(prev_button_x, prev_button_y, button_width, button_height)
            
            # Determine if previous button should be enabled based on current step
            prev_enabled = self.current_step != "class"
            
            # Store button rect for click detection
            self.navigation_buttons["prev"] = prev_button_rect if prev_enabled else None
            
            if prev_enabled:
                # Draw button background
                pygame.draw.rect(screen, (60, 80, 120), prev_button_rect)
                
                # Draw button border
                pygame.draw.rect(screen, (100, 140, 200), prev_button_rect, 2)
                
                # Draw button text
                prev_text = self.text_font.render("< Previous", True, (220, 220, 255))
                prev_text_rect = prev_text.get_rect(center=(
                    prev_button_x + button_width // 2,
                    prev_button_y + button_height // 2
                ))
                screen.blit(prev_text, prev_text_rect)
            
            # Next/Confirm button
            next_button_x = nav_region.x + nav_region.width - 50 - button_width
            next_button_y = nav_region.y + (nav_region.height - button_height) // 2
            
            # Create next button rect for click detection
            next_button_rect = pygame.Rect(next_button_x, next_button_y, button_width, button_height)
            
            # Determine button text and color based on current step
            if self.current_step == "summary":
                next_text = "Confirm"
                next_color = (80, 180, 80)  # Green for confirm
                border_color = (120, 220, 120)
            else:
                next_text = "Next >"
                next_color = (60, 80, 120)  # Blue for next
                border_color = (100, 140, 200)
            
            # Store button rect for click detection
            self.navigation_buttons["next"] = next_button_rect
            
            # Draw button background
            pygame.draw.rect(screen, next_color, next_button_rect)
            
            # Draw button border
            pygame.draw.rect(screen, border_color, next_button_rect, 2)
            
            # Draw button text
            next_text_surface = self.text_font.render(next_text, True, (220, 220, 255))
            next_text_rect = next_text_surface.get_rect(center=(
                next_button_x + button_width // 2,
                next_button_y + button_height // 2
            ))
            screen.blit(next_text_surface, next_text_rect)
            
            # Cancel button (smaller and less prominent)
            cancel_button_width = 100
            cancel_button_x = nav_region.x + nav_region.width // 2 - cancel_button_width // 2
            cancel_button_y = nav_region.y + (nav_region.height - button_height) // 2
            
            # Create cancel button rect for click detection
            cancel_button_rect = pygame.Rect(cancel_button_x, cancel_button_y, cancel_button_width, button_height)
            
            # Store button rect for click detection
            self.navigation_buttons["cancel"] = cancel_button_rect
            
            # Draw button background
            pygame.draw.rect(screen, (100, 60, 60), cancel_button_rect)
            
            # Draw button border
            pygame.draw.rect(screen, (150, 80, 80), cancel_button_rect, 2)
            
            # Draw button text
            cancel_text = self.text_font.render("Cancel", True, (220, 200, 200))
            cancel_text_rect = cancel_text.get_rect(center=(
                cancel_button_x + cancel_button_width // 2,
                cancel_button_y + button_height // 2
            ))
            screen.blit(cancel_text, cancel_text_rect)
        
        # Store button rects for click detection
        self.navigation_buttons = {
            "prev": prev_button_rect if prev_enabled else None,
            "next": next_button_rect,
            "cancel": cancel_button_rect
        }
            
    def _render_character_data(self, screen):
        """Render current character data (sidebar)."""
        # Display current selections in a sidebar
        sidebar_x = self.renderer.width - 250
        sidebar_y = 80
        sidebar_width = 230
        sidebar_height = 300
        
        if self.using_opengl:
            # Draw sidebar title
            sidebar_title = "Character"
            self.ui_renderer.render_text(
                sidebar_title, 
                self.text_font, 
                (200, 200, 255, 255),  # Text color
                sidebar_x + 10, sidebar_y + 10  # Position
            )
            
            # Draw character data
            y_offset = 50
            
            # Show character name
            name_text = f"Name: {self.character_data['name']}"
            self.ui_renderer.render_text(
                name_text,
                self.text_font,
                (220, 220, 220, 255),  # Text color
                sidebar_x + 10, sidebar_y + y_offset  # Position
            )
            y_offset += 30
            
            # Show character class
            class_text = "Class: "
            if self.character_data["class"] is not None:
                if isinstance(self.character_data["class"], dict) and "name" in self.character_data["class"]:
                    class_text += self.character_data["class"]["name"]
                else:
                    # Handle the case where class is just a string or other value
                    class_text += str(self.character_data["class"])
            else:
                class_text += "None"
            self.ui_renderer.render_text(
                class_text,
                self.text_font,
                (220, 220, 220, 255),  # Text color
                sidebar_x + 10, sidebar_y + y_offset  # Position
            )
            y_offset += 30
            
            # Show gender selection
            gender_text = f"Gender: {self.character_data['gender']}"
            self.ui_renderer.render_text(
                gender_text,
                self.text_font,
                (220, 220, 220, 255),  # Text color
                sidebar_x + 10, sidebar_y + y_offset  # Position
            )
            y_offset += 30
            
            # Show attributes header
            self.ui_renderer.render_text(
                "Attributes:",
                self.text_font,
                (200, 200, 255, 255),  # Text color
                sidebar_x + 10, sidebar_y + y_offset  # Position
            )
            y_offset += 20
            
            # Show attribute values
            for attr, value in self.character_data["attributes"].items():
                attr_text = f"  {attr.capitalize()}: {value}"
                self.ui_renderer.render_text(
                    attr_text,
                    self.text_font,
                    (220, 220, 220, 255),
                    sidebar_x + 10, sidebar_y + y_offset
                )
                y_offset += 20
            
        else:
            # Draw sidebar background with PyGame
            pygame.draw.rect(screen, (0, 0, 0, 128), (sidebar_x, sidebar_y, sidebar_width, sidebar_height))
            pygame.draw.rect(screen, (100, 100, 150), (sidebar_x, sidebar_y, sidebar_width, sidebar_height), 2)
        
            # Draw sidebar title
            sidebar_title = "Character"
            title_surface = self.text_font.render(sidebar_title, True, (200, 200, 255))
            screen.blit(title_surface, (sidebar_x + 10, sidebar_y + 10))
        
            # Draw character data
            y_offset = 50
        
            # Show character name
            name_text = f"Name: {self.character_data['name']}"
            text_surface = self.text_font.render(name_text, True, (220, 220, 220))
            screen.blit(text_surface, (sidebar_x + 10, sidebar_y + y_offset))
            y_offset += 30
            
            # Show character class
            class_text = "Class: "
            if self.character_data["class"] is not None:
                if isinstance(self.character_data["class"], dict) and "name" in self.character_data["class"]:
                    class_text += self.character_data["class"]["name"]
                else:
                    # Handle the case where class is just a string or other value
                    class_text += str(self.character_data["class"])
            else:
                class_text += "None"
            text_surface = self.text_font.render(class_text, True, (220, 220, 220))
            screen.blit(text_surface, (sidebar_x + 10, sidebar_y + y_offset))
            y_offset += 30
            
            # Show gender
            gender_text = f"Gender: {self.character_data['gender']}"
            text_surface = self.text_font.render(gender_text, True, (220, 220, 220))
            screen.blit(text_surface, (sidebar_x + 10, sidebar_y + y_offset))
            y_offset += 30
            
            # Show attributes header
            attr_header = "Attributes:"
            text_surface = self.text_font.render(attr_header, True, (200, 200, 255))
            screen.blit(text_surface, (sidebar_x + 10, sidebar_y + y_offset))
            y_offset += 20
            
            # Show attribute values
            for attr, value in self.character_data["attributes"].items():
                attr_text = f"{attr.capitalize()}: {value}"
                text_surface = self.text_font.render(attr_text, True, (220, 220, 220))
                screen.blit(text_surface, (sidebar_x + 20, sidebar_y + y_offset))
                y_offset += 20
        
    def _get_step_title(self):
        """Get the title for the current step."""
        if self.current_step == "class":
            return "Choose Your Class"
        elif self.current_step == "appearance":
            return "Customize Appearance"
        elif self.current_step == "attributes":
            return "Distribute Attributes"
        elif self.current_step == "background":
            return "Select Background"
        elif self.current_step == "name":
            return "Name Your Character"
        elif self.current_step == "equipment":
            return "Select Starting Equipment"
        elif self.current_step == "summary":
            return "Character Summary"
        return ""
        
    def _get_step_instructions(self):
        """Get instructions for the current step."""
        if self.current_step == "class":
            return "Select a character class that matches your preferred playstyle."
        elif self.current_step == "appearance":
            return "Customize your character's appearance."
        elif self.current_step == "attributes":
            return "Distribute 15 attribute points to define your character's strengths."
        elif self.current_step == "abilities":
            return "Choose special abilities for your character."
        elif self.current_step == "summary":
            return "Review your character before finalizing."
        return ""
        
    def handle_event(self, event):
        """
        Handle input events for character creation scene.
        
        Args:
            event: The pygame event to handle.
        
        Returns:
            bool: True if the event was consumed, False otherwise.
        """
        # Handle scroll wheel for content scrolling
        if event.type == pygame.MOUSEWHEEL:
            scroll_amount = event.y * 30  # Increase scroll speed to 30 pixels per wheel click
            self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset - scroll_amount))
            return True
            
        # Handle tab clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            mouse_pos = event.pos
            
            # Check if clicked on a tab
            for i, tab in enumerate(self.tab_buttons):
                if tab["rect"].collidepoint(mouse_pos):
                    self._switch_to_tab_index(i)
                    return True
            
        # Handle keyboard scrolling
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 30)
                return True
            elif event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - 30)
                return True
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 200)
                return True
            elif event.key == pygame.K_PAGEUP:
                self.scroll_offset = max(0, self.scroll_offset - 200)
                return True
            
            # Tab navigation
            elif event.key == pygame.K_TAB:
                # Shift+Tab goes backwards
                direction = -1 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
                self._switch_tab(direction)
                return True
                
            # Number keys for direct tab access
            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                index = event.key - pygame.K_1  # Convert key to 0-based index
                self._switch_to_tab_index(index)
                return True
            
            # Arrow keys with CTRL for tab navigation
            elif event.key == pygame.K_LEFT and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self._switch_tab(-1)
                return True
            elif event.key == pygame.K_RIGHT and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self._switch_tab(1)
                return True
            
            # Space or Enter to confirm a selection
            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self._confirm_selection()
                return True
                
        # Check for navigation button inputs (Back, Next, Cancel)
        if self._handle_navigation_input(event):
            return True
        
        # Handle different input based on the current step
        result = False  # Initialize result to False
        
        if self.current_step == "class":
            result = self._handle_class_input(event)
        elif self.current_step == "appearance":
            result = self._handle_appearance_input(event)
        elif self.current_step == "attributes":
            result = self._handle_attributes_input(event)
        elif self.current_step == "abilities":
            result = self._handle_abilities_input(event)
        elif self.current_step == "background":
            result = self._handle_background_input(event)
        elif self.current_step == "name":
            result = self._handle_name_input(event)
        elif self.current_step == "equipment":
            result = self._handle_equipment_input(event)
        elif self.current_step == "summary":
            result = self._handle_summary_input(event)
        
        if result:
            return True
        
        # Event wasn't handled
        return False
        
    def _handle_navigation_input(self, event):
        """Handle navigation button input."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            mouse_pos = event.pos
            
            # Debug navigation buttons
            print(f"Clicked at position: {mouse_pos}")
            print(f"Navigation buttons: {self.navigation_buttons}")
            
            # Check for navigation button clicks
            for button_name, button_rect in self.navigation_buttons.items():
                print(f"Checking button '{button_name}': {button_rect}")
                if button_rect and button_rect.collidepoint(mouse_pos):
                    print(f"Clicked on button: {button_name}")
                    if button_name == "prev":
                        self._go_to_previous_step()
                        return True
                elif button_name == "next":
                    if self.current_step == "summary":
                        self._complete_character_creation()
                    else:
                        self._go_to_next_step()
                        return True
                elif button_name == "cancel":
                    print("Cancel button clicked, calling _cancel_creation()")
                    self._cancel_creation()
                    return True
        
        # Check for keyboard navigation
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._cancel_creation()
                return True
            elif event.key == pygame.K_RETURN and pygame.key.get_mods() & pygame.KMOD_CTRL:
                # Ctrl+Enter to confirm and go to next step
                if self.current_step == "summary":
                    self._complete_character_creation()
                else:
                    self._go_to_next_step()
                return True
        
        return False
        
    def _go_to_previous_step(self):
        """Go to the previous character creation step."""
        if self.current_step == "name":
            self.current_step = "class"
        elif self.current_step == "appearance":
            self.current_step = "name"
        elif self.current_step == "attributes":
            self.current_step = "appearance"
        elif self.current_step == "abilities":
            self.current_step = "attributes"
        elif self.current_step == "background":
            self.current_step = "abilities"
        elif self.current_step == "summary":
            self.current_step = "background"
        
    def _go_to_next_step(self):
        """Go to the next character creation step."""
        if self.current_step == "class":
            self.current_step = "name"
            self._setup_name_selection()  # Make sure the name UI is set up
        elif self.current_step == "name":
            self.current_step = "appearance"
        elif self.current_step == "appearance":
            self.current_step = "attributes"
        elif self.current_step == "attributes":
            self.current_step = "abilities"
        elif self.current_step == "abilities":
            self.current_step = "background"
        elif self.current_step == "background":
            self.current_step = "summary"
        
    def _handle_attributes_input(self, event):
        """Handle input for attribute distribution step."""
        # Handle mouse clicks on +/- buttons
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            mouse_pos = event.pos
            
            # Check for click on reset button
            if hasattr(self, 'reset_attr_button') and self.reset_attr_button.collidepoint(mouse_pos):
                # Reset all attributes to default (8)
                for attr_info in self.attribute_options:
                    current_value = attr_info["get"]()
                    default_value = 8
                    # Calculate how many points to refund
                    point_change = current_value - default_value 
                    # Update available points
                    self.available_attribute_points += point_change
                    # Set to default
                    attr_info["set"](default_value)
                return True
            
            for attr_info in self.attribute_options:
                # Check for click on minus button
                if "minus_rect" in attr_info and attr_info["minus_rect"].collidepoint(mouse_pos):
                    current_value = attr_info["get"]()
                    
                    # Decrease value if not at minimum
                    if current_value > attr_info["min"]:
                        attr_info["set"](current_value - 1)
                        # Refund a point when decreasing
                        self.available_attribute_points += 1
                        return True
                
                # Check for click on plus button
                if "plus_rect" in attr_info and attr_info["plus_rect"].collidepoint(mouse_pos):
                    current_value = attr_info["get"]()
                    
                    # Increase value if not at maximum and we have points available
                    if current_value < attr_info["max"] and self.available_attribute_points > 0:
                        attr_info["set"](current_value + 1)
                        # Spend a point when increasing
                        self.available_attribute_points -= 1
                        return True
        
        # Handle keyboard input for attribute adjustment
        if event.type == pygame.KEYDOWN:
            options = self.attribute_options
            if 0 <= self.selected_option < len(options):
                option = options[self.selected_option]
                
                # Decrease attribute with left arrow
                if event.key == pygame.K_LEFT:
                    current_value = option["get"]()
                    if current_value > option["min"]:
                        option["set"](current_value - 1)
                        # Refund a point when decreasing
                        self.available_attribute_points += 1
                        return True
                        
                # Increase attribute with right arrow
                elif event.key == pygame.K_RIGHT:
                    current_value = option["get"]()
                    if current_value < option["max"] and self.available_attribute_points > 0:
                        option["set"](current_value + 1)
                        # Spend a point when increasing
                        self.available_attribute_points -= 1
                        return True
        
        return False
        
    def _handle_background_input(self, event):
        """Handle input for background selection."""
        # Check for mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            mouse_pos = event.pos
            
            # Check for clicks on background options
            for background in self.background_options:
                if "rect" in background and background["rect"].collidepoint(mouse_pos):
                    # Set the selected background
                    self.character_data["background"] = background["id"]
                    return True
            
        return False
        
    def _handle_name_input(self, event):
        """Handle input for name selection step."""
        # Handle mouse clicks on UI elements
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check for clicks on the random name button
            if hasattr(self, 'random_name_button_rect') and self.random_name_button_rect.collidepoint(event.pos):
                self._generate_random_name()
                return True
                
        # Handle keyboard input
        if event.type == pygame.KEYDOWN:
            # Handle text input for name
            if event.key == pygame.K_BACKSPACE:
                # Remove last character
                self.character_data["name"] = self.character_data["name"][:-1]
                return True
            elif event.key == pygame.K_RETURN:
                # Proceed to next step
                self._go_to_next_step()
                return True
            elif len(event.unicode) > 0 and event.unicode.isprintable():
                # Only allow letters, numbers, and spaces
                valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '-"
                if event.unicode in valid_chars and len(self.character_data["name"]) < 20:
                    # Add character to name
                    self.character_data["name"] += event.unicode
                    return True
                
        return False
        
    def _handle_equipment_input(self, event):
        """Handle input for equipment selection step."""
        # In a real implementation, this would handle equipment selection controls
        return False
        
    def _handle_summary_input(self, event):
        """Handle input for summary step."""
        # In a real implementation, this would handle the confirmation button
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self._complete_character_creation()
            return True
            
        return False
        
    def _complete_character_creation(self):
        """Complete character creation and start the game."""
        # Print character data for debugging
        class_info = "None"
        if self.character_data["class"] is not None:
            if isinstance(self.character_data["class"], dict) and "name" in self.character_data["class"]:
                class_info = self.character_data["class"]["name"]
            else:
                class_info = str(self.character_data["class"])
                
        print(f"Created character: {self.character_data['name']}, {class_info}")
        
        # For now, just return to the main menu since we don't have a GameScene yet
        # This is a simplified implementation - in a real game, we would transition to the actual game world
        # Call the callback if provided
        if self.on_character_created:
            self.on_character_created(self.character_data)
            print(f"Character creation complete: {self.character_data['name']}")
            return
            
        # If no callback is defined, we can't safely continue - just quit the scene
        print("Warning: No callback defined for character creation completion")
        pygame.event.post(pygame.event.Event(pygame.QUIT))
            
    def load(self):
        """Called when the scene becomes active."""
        super().load()
        print("Loading Character Creation Scene")
        
    def unload(self):
        """Called when the scene is deactivated."""
        print("Unloading Character Creation Scene")
        super().unload()
        
    def _update_preview_character(self):
        """Update the character preview based on current settings."""
        # Clear the preview surface
        self.preview_surface.fill((40, 40, 60))
        
        # Generate character sprite if procedural generator is available
        if self.procedural_generator and not self.assets_generated:
            try:
                # Generate character based on current settings
                self.procedural_generator.generate_character(
                    gender=self.character_data["gender"],
                    skin_tone=self.character_data["appearance"]["skin_tone"],
                    hair_style=self.character_data["appearance"]["hair_style"],
                    hair_color=self.character_data["appearance"]["hair_color"],
                    face_style=self.character_data["appearance"]["face_style"],
                    body_type=self.character_data["appearance"]["body_type"]
                )
                
                # Assets have been generated
                self.assets_generated = True
                
            except Exception as e:
                print(f"Error generating character: {e}")
                
        # Try to load the character sprite
        sprite_path = self._get_character_sprite_path()
        
        if os.path.exists(sprite_path):
            try:
                self.character_sprite = pygame.image.load(sprite_path)
                self.character_sprite = pygame.transform.scale(self.character_sprite, (200, 300))
                self.preview_surface.blit(self.character_sprite, (50, 50))
            except Exception as e:
                print(f"Error loading character sprite: {e}")
                self._draw_placeholder_character()
        else:
            self._draw_placeholder_character()
            
    def _get_character_sprite_path(self):
        """Get the path to the character sprite based on current settings."""
        gender = self.character_data["gender"]
        char_class = self.character_data["class"]
        
        # Gender-specific sprite path
        sprite_path = os.path.join("assets", "sprites", "player", gender, f"{char_class}_idle.png")
        
        # If class-specific sprite doesn't exist, use default
        if not os.path.exists(sprite_path):
            sprite_path = os.path.join("assets", "sprites", "player", gender, "default_idle.png")
            
        return sprite_path
        
    def _draw_placeholder_character(self):
        """Draw a placeholder character when sprite is not available."""
        # Get appearance settings
        gender = self.character_data["gender"]
        skin_tone = self.character_data["appearance"]["skin_tone"]
        body_type = self.character_data["appearance"]["body_type"]
        hair_style = self.character_data["appearance"]["hair_style"]
        hair_color = self.character_data["appearance"]["hair_color"]
        
        # Determine skin color based on skin tone
        skin_colors = [
            (255, 224, 196),  # Pale
            (241, 194, 167),  # Light
            (224, 172, 138),  # Tan
            (141, 85, 63)     # Dark
        ]
        skin_color = skin_colors[min(skin_tone, len(skin_colors)-1)]
        
        # Determine hair color
        hair_colors = [
            (30, 30, 30),      # Black
            (96, 54, 29),      # Brown
            (222, 184, 135),   # Blonde
            (155, 69, 49),     # Red
            (160, 160, 160),   # Gray
            (240, 240, 240)    # White
        ]
        hair_color = hair_colors[min(self.character_data["appearance"]["hair_color"], len(hair_colors)-1)]
        
        # Clear the background
        self.preview_surface.fill((40, 40, 60))
        
        # Adjust body proportions based on gender and body type
        head_size = 50
        
        # Female characters have slightly different proportions
        if gender == "female":
            shoulder_width = 70 if body_type == 1 else 60  # Narrower for non-athletic
            hip_width = 70
            waist_width = 50
        else:  # Male
            shoulder_width = 80 if body_type == 1 else 70  # Wider for athletic
            hip_width = 60
            waist_width = 60 if body_type == 1 else 50  # Athletic or average
        
        # Adjust based on body type (slimmer, average, athletic)
        if body_type == 2:  # Slim
            shoulder_width -= 10
            hip_width -= 5
            waist_width -= 10
        
        # Center point for the character
        center_x = self.preview_surface.get_width() // 2
        top_y = 70
        
        # Head (circle)
        pygame.draw.ellipse(self.preview_surface, skin_color, 
                          (center_x - head_size//2, top_y, head_size, head_size))
        
        # Hair (depends on style)
        if hair_style != 5:  # Not bald
            # Different hair styles
            if hair_style == 0:  # Short
                pygame.draw.ellipse(self.preview_surface, hair_color,
                                  (center_x - head_size//2 - 5, top_y - 10, head_size + 10, head_size//2))
            elif hair_style == 1:  # Medium
                pygame.draw.ellipse(self.preview_surface, hair_color,
                                  (center_x - head_size//2 - 8, top_y - 10, head_size + 16, head_size//2 + 10))
            elif hair_style == 2:  # Long
                pygame.draw.ellipse(self.preview_surface, hair_color,
                                  (center_x - head_size//2 - 10, top_y - 10, head_size + 20, head_size//2 + 5))
                # Long hair strands
                pygame.draw.rect(self.preview_surface, hair_color,
                               (center_x - head_size//3, top_y + head_size - 5, head_size//3*2, head_size))
            elif hair_style in [3, 4]:  # Curly or wavy
                for i in range(6):
                    offset_x = (i - 3) * 10
                    offset_y = 5 if i % 2 == 0 else 0
                    pygame.draw.circle(self.preview_surface, hair_color,
                                     (center_x + offset_x, top_y + offset_y), 12)
        
        # Neck
        neck_width = 20
        neck_height = 20
        pygame.draw.rect(self.preview_surface, skin_color,
                       (center_x - neck_width//2, top_y + head_size, neck_width, neck_height))
        
        # Torso (trapezoid shape for more realistic body)
        torso_height = 100
        
        # Create polygon points for the torso
        torso_points = [
            (center_x - shoulder_width//2, top_y + head_size + neck_height),  # Top left
            (center_x + shoulder_width//2, top_y + head_size + neck_height),  # Top right
            (center_x + waist_width//2, top_y + head_size + neck_height + torso_height),  # Bottom right
            (center_x - waist_width//2, top_y + head_size + neck_height + torso_height)   # Bottom left
        ]
        
        # Draw torso
        # Use a slightly darker color for clothing
        cloth_color = (100, 100, 150)
        pygame.draw.polygon(self.preview_surface, cloth_color, torso_points)
        
        # Legs
        leg_width = 20
        leg_height = 80
        leg_spacing = 10
        
        # Left leg
        pygame.draw.rect(self.preview_surface, cloth_color,
                       (center_x - leg_width - leg_spacing//2, 
                        top_y + head_size + neck_height + torso_height, 
                        leg_width, leg_height))
        
        # Right leg
        pygame.draw.rect(self.preview_surface, cloth_color,
                       (center_x + leg_spacing//2, 
                        top_y + head_size + neck_height + torso_height, 
                        leg_width, leg_height))
        
        # Arms (adjust based on body type)
        arm_width = 15
        arm_length = 80
        
        # Left arm
        pygame.draw.rect(self.preview_surface, skin_color,
                       (center_x - shoulder_width//2, 
                        top_y + head_size + neck_height, 
                        arm_width, arm_length))
        
        # Right arm
        pygame.draw.rect(self.preview_surface, skin_color,
                       (center_x + shoulder_width//2 - arm_width, 
                        top_y + head_size + neck_height, 
                        arm_width, arm_length))
                        
        # Add a simple facial feature
        eye_size = 5
        eye_y = top_y + head_size//2 - 5
        # Left eye
        pygame.draw.circle(self.preview_surface, (30, 30, 30),
                         (center_x - 10, eye_y), eye_size)
        # Right eye
        pygame.draw.circle(self.preview_surface, (30, 30, 30),
                         (center_x + 10, eye_y), eye_size)
        
        # Simple mouth
        pygame.draw.arc(self.preview_surface, (150, 70, 70),
                       (center_x - 15, eye_y + 15, 30, 20), 0, 3.14, 2)
        
    def _set_character_property(self, prop, value):
        """Set a top-level character property."""
        if prop in self.character_data:
            self.character_data[prop] = value
            self._update_preview_character()
            
    def _set_appearance_property(self, prop, value):
        """Set a character appearance property."""
        if prop in self.character_data["appearance"]:
            self.character_data["appearance"][prop] = value
            self._update_preview_character()
            
    def _set_attribute_property(self, prop, value):
        """Set a character attribute property."""
        if prop in self.character_data["attributes"]:
            self.character_data["attributes"][prop] = value
            
    def _get_current_options(self):
        """Get options for the current tab."""
        if self.active_tab == "appearance":
            return self.appearance_options
        elif self.active_tab == "attributes":
            return self.attribute_options
        elif self.active_tab == "abilities":
            return self.ability_options
        elif self.active_tab == "background":
            return self.background_options
        return []
        
    def _cancel_creation(self):
        """Cancel character creation and go back to main menu."""
        print("Character creation cancelled")
        
        # Create a stack trace to see the call hierarchy
        import traceback
        traceback.print_stack()
        
        # Try multiple ways to get back to the main menu
        try:
            # Method 1: Direct engine reference on world
            if hasattr(self.world, 'engine'):
                print("Using world.engine to return to main menu")
                self.world.engine.show_main_menu()
                return
                
            # Method 2: Engine reference on UI manager
            if hasattr(self.ui_manager, 'engine'):
                print("Using ui_manager.engine to return to main menu")
                self.ui_manager.engine.show_main_menu()
                return
                
            # Method 3: Try to find any engine reference
            if hasattr(self, 'engine'):
                print("Using self.engine to return to main menu")
                self.engine.show_main_menu()
                return
                
            # Method 4: Use scene manager
            if hasattr(self.world, 'scene_manager'):
                print("Using scene_manager to return to main menu")
                from ...ui.menus.main_menu import MainMenu
                main_menu = MainMenu(self.world, self.renderer, self.ui_manager)
                self.world.scene_manager.set_active_scene(main_menu)
                return
                
            # Method 5: Try getting scene manager from world
            for attr_name in dir(self.world):
                attr = getattr(self.world, attr_name)
                if hasattr(attr, 'set_active_scene'):
                    print(f"Found scene manager in world.{attr_name}")
                    from ...ui.menus.main_menu import MainMenu
                    main_menu = MainMenu(self.world, self.renderer, self.ui_manager)
                    attr.set_active_scene(main_menu)
                    return
                
            # Method 6: Use global engine instance if available
            import sys
            for module_name in sys.modules:
                module = sys.modules[module_name]
                if hasattr(module, 'engine') and hasattr(module.engine, 'show_main_menu'):
                    print(f"Using global engine instance from {module_name}")
                    module.engine.show_main_menu()
                    return
            
            print("WARNING: Could not find a way to return to main menu")
            
        except Exception as e:
            print(f"Error trying to return to main menu: {e}")
            import traceback
            traceback.print_exc()
        
    def _create_character(self):
        """Create the character and start the game."""
        # Create player entity with specified attributes
        
        # Call the creation callback if provided
        if self.on_character_created:
            self.on_character_created(self.character_data)
            
    def update(self, dt: float):
        """Update the character creation scene."""
        # Update input cooldown
        if self.input_cooldown > 0:
            self.input_cooldown -= dt
            
        # Process input for selection and navigation
        keys = pygame.key.get_pressed()
        
        if self.input_cooldown <= 0:
            if keys[pygame.K_UP]:
                self.selected_option = max(0, self.selected_option - 1)
                self.input_cooldown = 0.2
            elif keys[pygame.K_DOWN]:
                options = self._get_current_options()
                self.selected_option = min(len(options) - 1, self.selected_option + 1)
                self.input_cooldown = 0.2
            elif keys[pygame.K_LEFT]:
                self._adjust_selected_option(-1)
                self.input_cooldown = 0.2
            elif keys[pygame.K_RIGHT]:
                self._adjust_selected_option(1)
                self.input_cooldown = 0.2
            elif keys[pygame.K_TAB]:
                self._switch_tab()
                self.input_cooldown = 0.2
            elif keys[pygame.K_RETURN]:
                self._confirm_selection()
                self.input_cooldown = 0.2
                
    def _adjust_selected_option(self, direction):
        """Adjust the value of the selected option."""
        options = self._get_current_options()
        if self.selected_option < 0 or self.selected_option >= len(options):
            return
            
        option = options[self.selected_option]
        
        if "values" in option:
            # For options with predefined values
            current_idx = option["values"].index(option["get"]()) if option["get"]() in option["values"] else 0
            new_idx = (current_idx + direction) % len(option["values"])
            option["set"](option["values"][new_idx])
        elif "min" in option and "max" in option:
            # For numeric options
            current_val = option["get"]()
            new_val = max(option["min"], min(option["max"], current_val + direction))
            option["set"](new_val)
            
    def _switch_tab(self, direction=1):
        """Switch to the next tab."""
        tabs = ["appearance", "attributes", "abilities", "background"]
        current_idx = tabs.index(self.active_tab) if self.active_tab in tabs else 0
        self.active_tab = tabs[(current_idx + direction) % len(tabs)]
        self.selected_option = 0
        print(f"Switched to tab: {self.active_tab}")
        
    def _confirm_selection(self):
        """Confirm current selection or perform action."""
        # Get current mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Check navigation buttons
        for button_name, button_rect in self.navigation_buttons.items():
            if button_rect and button_rect.collidepoint(mouse_pos):
                if button_name == "prev":
                    self._go_to_previous_step()
                    return
                elif button_name == "next":
                    if self.current_step == "summary":
                        self._complete_character_creation()
                    else:
                        self._go_to_next_step()
                    return
                elif button_name == "cancel":
                    self._cancel_creation()
                    return
        
        # Check control buttons
        for button in self.control_buttons:
            if "rect" in button and button["rect"].collidepoint(mouse_pos):
                if "action" in button:
                    button["action"]()
                    return

    def _wrap_text(self, text, font, max_width):
        """Wrap text to fit within a given width."""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            # Create test line with a new word
            test_line = current_line + [word]
            test_text = ' '.join(test_line)
            
            # Check if test line exceeds max width
            if font.size(test_text)[0] <= max_width:
                current_line = test_line
            else:
                # Start a new line if current one is too long
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        # Add the last line
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines

    def _update_abilities_for_class(self):
        """Update available abilities based on selected character class."""
        self.ability_options = []
        
        # Check if class is selected
        if self.character_data["class"] is None:
            return
            
        # Get the selected class 
        selected_class = self.character_data["class"]
        
        # Use the Character class to get abilities for the given class type
        if isinstance(selected_class, dict) and "enum" in selected_class:
            try:
                char_instance = Character(selected_class["enum"])
                
                # Convert abilities dict to our format
                for ability_id, ability in char_instance.abilities.items():
                    # Get a descriptive display text for the ability type
                    type_display = str(ability.type.value).capitalize()
                    
                    # Create color-coded and formatted description based on ability type
                    description_detail = ""
                    if ability.type == AbilityType.PHYSICAL:
                        description_detail = f"Physical damage: {ability.base_power}"
                    elif ability.type == AbilityType.MAGICAL:
                        description_detail = f"Magical damage: {ability.base_power}"
                    elif ability.type == AbilityType.HYBRID:
                        description_detail = f"Hybrid damage: {ability.base_power}"
                    elif ability.type == AbilityType.BUFF:
                        description_detail = "Enhances character stats"
                    elif ability.type == AbilityType.DEBUFF:
                        description_detail = "Weakens enemies"
                    elif ability.type == AbilityType.SUMMON:
                        description_detail = "Summons ally to fight"
                    
                    # Format with cooldown information
                    full_description = f"{ability.name}: {type_display} - {description_detail} (Cooldown: {ability.cooldown}s)"
                    
                    self.ability_options.append({
                        "name": ability.name,
                        "type": ability.type,
                        "description": full_description,
                        "power": ability.base_power,
                        "cooldown": ability.cooldown,
                        "fx_type": ability.fx_type
                    })
                
                # If we successfully loaded abilities, return here - don't overwrite with generic ones
                if self.ability_options:
                    print(f"Successfully loaded {len(self.ability_options)} abilities for {selected_class['enum']}")
                    return
            
            except Exception as e:
                print(f"Error creating Character instance: {e}")
                # Fall through to generic abilities on error
                
        # Fallback to generic abilities only if we couldn't load class-specific ones
        print("Using generic abilities as fallback")
        self.ability_options = [
                {"name": "Basic Attack", "type": AbilityType.PHYSICAL, "description": "A simple attack"},
                {"name": "Defensive Stance", "type": AbilityType.BUFF, "description": "Increase defense temporarily"}
            ]

    def _adjust_appearance_option(self, direction):
        """Adjust the currently selected appearance option."""
        options = self.appearance_options
        if 0 <= self.selected_option < len(options):
            option = options[self.selected_option]
            current_value = option["get"]()
            
            if isinstance(current_value, int):
                # For integer-indexed values (skin tone, hair style, etc.)
                max_value = len(option["values"]) - 1
                new_value = (current_value + direction) % (max_value + 1)
                option["set"](new_value)
            else:
                # For non-integer values (gender, etc.)
                values = option["values"]
                if current_value in values:
                    current_index = values.index(current_value)
                    new_index = (current_index + direction) % len(values)
                    option["set"](values[new_index])
                    
    def _adjust_attribute_option(self, direction):
        """Adjust the currently selected attribute value."""
        options = self.attribute_options
        if 0 <= self.selected_option < len(options):
            option = options[self.selected_option]
            current_value = option["get"]()
            
            # Calculate new value with limits
            min_value = option["min"]
            max_value = option["max"]
            new_value = max(min_value, min(max_value, current_value + direction))
            
            # No change needed if the value didn't change
            if new_value == current_value:
                return
            
            # Check if we have enough points to increase
            if direction > 0 and self.available_attribute_points <= 0:
                # Not enough points to increase
                return
            
            # Calculate point cost/refund
            point_change = current_value - new_value
            
            # Update available points
            self.available_attribute_points += point_change
            
            # Set the new value
            option["set"](new_value)

    def _render_appearance_tab(self, screen, content_x, content_y):
        """Render the appearance tab content with appearance options."""
        if self.using_opengl:
            # Calculate main content dimensions
            content_width = self.ui_regions["main_content"].width
            content_height = self.ui_regions["main_content"].height
            
            # Apply scroll offset
            adjusted_y = content_y - self.scroll_offset
            
            # Instructions at the top
            instruction_text = "Customize your character's appearance"
            self.ui_renderer.render_text(
                instruction_text,
                self.small_font,
                (200, 200, 220, 220),
                content_x + content_width // 2 - len(instruction_text) * 3, adjusted_y
            )
            
            # Add a note about appearance changes
            note_text = "Changes will be reflected in the character preview"
            self.ui_renderer.render_text(
                note_text,
                self.small_font,
                (180, 180, 200, 200),
                content_x + content_width // 2 - len(note_text) * 3, adjusted_y + 20
            )
            
            # Display character summary section
            self._render_character_summary(content_x, adjusted_y + 50, content_width)
            
            # Split options into two columns
            col_width = (content_width - 60) // 2
            
            # Get the appearance options for the left and right column
            left_column_options = self.appearance_options[:3]  # First three options
            right_column_options = self.appearance_options[3:]  # Remaining options
            
            # Render left and right columns
            self._render_appearance_column(left_column_options, content_x, adjusted_y + 140, col_width)
            self._render_appearance_column(right_column_options, content_x + col_width + 40, adjusted_y + 140, col_width)
            
            # Calculate total content height for scrolling
            total_content_height = 140 + max(len(left_column_options), len(right_column_options)) * 70 + 50
            self.max_scroll = max(0, total_content_height - content_height)
        else:
            # PyGame fallback implementation
            pass
    
    def _render_appearance_column(self, options, col_x, start_y, col_width):
        """Render a column of appearance options."""
        option_height = 70
        option_spacing = 60
        
        # Calculate content Y range (for skipping non-visible items)
        content_y = self.ui_regions["main_content"].y
        content_height = self.ui_regions["main_content"].height
        visible_range_min = content_y
        visible_range_max = content_y + content_height
        
        for i, option in enumerate(options):
            # Calculate option's absolute position (including scroll)
            option_abs_y = start_y + i * option_spacing
            
            # Skip rendering if the option is completely outside the visible area
            if (option_abs_y + option_height < visible_range_min - self.scroll_offset or
                option_abs_y > visible_range_max - self.scroll_offset):
                # Set the button rects to None since they're not on screen
                option["left_rect"] = None
                option["right_rect"] = None
                option["option_rect"] = None
                continue
                
            # Draw option name
            self.ui_renderer.render_text(
                option["text"],
                self.text_font,
                (220, 220, 255, 255),
                col_x, option_abs_y
            )
            
            # Draw option controls
            control_y = option_abs_y + 30
            control_width = col_width - 30
            
            # Get current value
            current_value = option["get"]()
            
            # Draw a box around the control area
            self.ui_renderer.draw_rectangle(
                col_x, control_y,
                control_width, 30,
                (50, 50, 70, 100)
            )
            
            # Draw left arrow button
            arrow_btn_size = 30
            left_arrow_x = col_x
            left_arrow_y = control_y
            
            # Store the button rect for interaction (adjusted for actual screen position without scroll offset)
            # We need to calculate the actual y coordinate on screen
            screen_y = content_y + (option_abs_y - (content_y - self.scroll_offset)) + 30
            
            # Store the actual button rects for interaction checking
            option["left_rect"] = pygame.Rect(left_arrow_x, screen_y, arrow_btn_size, arrow_btn_size)
            option["option_rect"] = pygame.Rect(col_x, screen_y - 30, control_width, 60)
            
            # Draw left arrow button
            self.ui_renderer.draw_rectangle(
                left_arrow_x, left_arrow_y,
                arrow_btn_size, arrow_btn_size,
                (80, 80, 100, 150)
            )
            self.ui_renderer.render_text(
                "<",
                self.text_font,
                (220, 220, 255, 255),
                left_arrow_x + 10, left_arrow_y + 5
            )
            
            # Draw current value text
            value_text = self._get_appearance_value_display(option["property"], current_value)
            value_x = col_x + (control_width - len(value_text) * 8) // 2
            self.ui_renderer.render_text(
                value_text,
                self.text_font,
                (255, 255, 255, 255),
                value_x, control_y + 5
            )
            
            # Draw right arrow button
            right_arrow_x = col_x + control_width - arrow_btn_size
            right_arrow_y = control_y
            
            # Store the button rect for interaction (adjusted for actual screen position)
            option["right_rect"] = pygame.Rect(right_arrow_x, screen_y, arrow_btn_size, arrow_btn_size)
            
            # Draw right arrow button
            self.ui_renderer.draw_rectangle(
                right_arrow_x, right_arrow_y,
                arrow_btn_size, arrow_btn_size,
                (80, 80, 100, 150)
            )
            self.ui_renderer.render_text(
                ">",
                self.text_font,
                (220, 220, 255, 255),
                right_arrow_x + 10, right_arrow_y + 5
            )

    def _get_appearance_value_display(self, property_name, value):
        """Get a user-friendly display string for an appearance value."""
        # The property_name is already passed as a string, no need to extract it from an option dictionary
        
        if property_name == "gender":
            return value.capitalize()
        elif property_name == "skin_tone":
            tones = ["Pale", "Light", "Tan", "Dark"]
            return tones[min(value, len(tones)-1)]
        elif property_name == "hair_style":
            styles = ["Short", "Medium", "Long", "Curly", "Wavy", "Bald"]
            return styles[min(value, len(styles)-1)]
        elif property_name == "hair_color":
            colors = ["Black", "Brown", "Blonde", "Red", "Gray", "White"]
            return colors[min(value, len(colors)-1)]
        elif property_name == "face_style":
            styles = ["Round", "Oval", "Square", "Heart"]
            return styles[min(value, len(styles)-1)]
        elif property_name == "body_type":
            types = ["Average", "Athletic", "Slim"]
            return types[min(value, len(types)-1)]
        
        # Default: just return the value as a string
        return str(value)

    def _render_attributes_tab(self, screen, content_x, content_y):
        """Render the attributes tab content with attribute distribution options."""
        if self.using_opengl:
            # Get main content dimensions
            content_width = self.ui_regions["main_content"].width
            content_height = self.ui_regions["main_content"].height
            
            # Apply scroll offset
            adjusted_y = content_y - self.scroll_offset
            
            # Instructions at the top
            instruction_text = "Distribute points among your character's attributes"
            self.ui_renderer.render_text(
                instruction_text,
                self.small_font,
                (200, 200, 220, 220),
                content_x + content_width // 2 - len(instruction_text) * 3, adjusted_y
            )
            
            # Display available points with more prominent styling
            points_color = (255, 255, 150, 255) if self.available_attribute_points > 0 else (180, 180, 180, 255)
            points_text = f"Available Points: {self.available_attribute_points}"
            
            # Draw highlight box around points if available
            if self.available_attribute_points > 0:
                self.ui_renderer.draw_rectangle(
                    content_x + content_width // 2 - 100, adjusted_y + 25,
                    200, 30,
                    (80, 80, 40, 100)
                )
            
            # Position the points counter more centrally
            self.ui_renderer.render_text(
                points_text,
                self.text_font,
                points_color,
                content_x + content_width // 2 - len(points_text) * 4, adjusted_y + 30
            )
            
            # Add reset button for attributes
            reset_btn_width = 80
            reset_btn_height = 30
            reset_btn_x = content_x + content_width // 2 + 80
            reset_btn_y = adjusted_y + 30
            
            # Draw reset button
            reset_btn_color = (100, 100, 150, 200)
            self.ui_renderer.draw_rectangle(
                reset_btn_x, reset_btn_y,
                reset_btn_width, reset_btn_height,
                reset_btn_color
            )
            
            # Store reset button rectangle for click detection
            # Adjust for scroll position when storing rect for click detection
            self.reset_attr_button = pygame.Rect(reset_btn_x, content_y + 30, reset_btn_width, reset_btn_height)
            
            # Draw button text
            self.ui_renderer.render_text(
                "Reset",
                self.small_font,
                (220, 220, 255, 255),
                reset_btn_x + 20, reset_btn_y + 8
            )
            
            # Display character summary section
            self._render_character_summary(content_x, adjusted_y + 70, content_width)
            
            # Render attribute controls
            attr_section_y = adjusted_y + 170
            attr_height = 50
            attr_width = content_width - 40
            
            # Initialize attribute info objects if they don't exist
            if not hasattr(self, 'attribute_options') or not self.attribute_options:
                self._setup_attribute_distribution()
            
            for i, attr_info in enumerate(self.attribute_options):
                # Check if we have all required keys in the attribute_info
                if not all(key in attr_info for key in ['text', 'property', 'min', 'max', 'get', 'set']):
                    continue
                
                # Calculate Y position with scrolling
                attr_y = attr_section_y + i * attr_height
                
                # Skip if outside the visible area
                if (attr_y + attr_height < self.ui_regions["content"].y or 
                    attr_y > self.ui_regions["content"].y + self.ui_regions["content"].height):
                    continue
                
                # Get current value
                current_value = attr_info["get"]()
                
                # Draw attribute background (alternate colors for better readability)
                bg_color = (50, 50, 70, 100) if i % 2 == 0 else (40, 40, 60, 100)
                
                # Draw attribute row background
                self.ui_renderer.draw_rectangle(
                    content_x, attr_y,
                    attr_width, attr_height - 5,
                    bg_color
                )
                
                # Draw attribute name
                self.ui_renderer.render_text(
                    attr_info["text"],
                    self.text_font,
                    (255, 255, 255, 255),
                    content_x + 10, attr_y + 5
                )
                
                # Draw description
                if "description" in attr_info:
                    self.ui_renderer.render_text(
                        attr_info["description"],
                        self.small_font,
                        (200, 200, 220, 200),
                        content_x + 120, attr_y + 15
                    )
                
                # Calculate positions for buttons and value
                attr_value_x = content_x + attr_width - 80
                minus_x = attr_value_x - 40
                plus_x = attr_value_x + 40
                
                # Store button rectangles for interaction
                # Adjust for scroll position when storing rects for click detection
                attr_info["minus_rect"] = pygame.Rect(minus_x - 15, content_y + 170 + i * attr_height + 10, 30, 30)
                attr_info["plus_rect"] = pygame.Rect(plus_x - 15, content_y + 170 + i * attr_height + 10, 30, 30)
                
                # Draw minus button with visual indication of disabled state
                can_decrease = current_value > attr_info["min"]
                minus_color = (255, 100, 100, 255) if can_decrease else (100, 100, 100, 150)
                self.ui_renderer.draw_rectangle(
                    minus_x - 15, attr_y + 10,
                    30, 30,
                    minus_color
                )
                self.ui_renderer.render_text(
                    "-",
                    self.text_font,
                    (220, 220, 255, 255),
                    minus_x, attr_y + 15
                )
                
                # Draw current value
                self.ui_renderer.render_text(
                    str(current_value),
                    self.text_font,
                    (255, 255, 255, 255),
                    attr_value_x, attr_y + 15
                )
                
                # Draw plus button with visual indication of disabled state
                can_increase = current_value < attr_info["max"] and self.available_attribute_points > 0
                plus_color = (100, 255, 100, 255) if can_increase else (100, 100, 100, 150)
                self.ui_renderer.draw_rectangle(
                    plus_x - 15, attr_y + 10,
                    30, 30,
                    plus_color
                )
                self.ui_renderer.render_text(
                    "+",
                    self.text_font,
                    (220, 220, 255, 255),
                    plus_x, attr_y + 15
                )
            
            # Update the max scroll value based on content height
            max_content_height = attr_section_y + len(self.attribute_options) * attr_height + 50
            self.max_scroll = max(0, max_content_height - content_height)
        else:
            # PyGame fallback rendering
            pass
    
    def _render_background_tab(self, screen, content_x, content_y):
        """Render the background tab content with character background options."""
        if self.using_opengl:
            # Get main content dimensions
            content_width = self.ui_regions["main_content"].width
            content_height = self.ui_regions["main_content"].height
            
            # Apply scroll offset
            adjusted_y = content_y - self.scroll_offset
            
            # Instructions at the top
            instruction_text = "Choose a background story for your character"
            self.ui_renderer.render_text(
                instruction_text,
                self.small_font,
                (200, 200, 220, 220),
                content_x + content_width // 2 - len(instruction_text) * 3, adjusted_y
            )
            
            # Check if we have background options loaded
            if not self.background_options:
                # Try to load backgrounds
                self._load_backgrounds()
                
            if not self.background_options:
                # Default backgrounds if none are loaded
                self.background_options = [
                    {"id": "street_urchin", "name": "Street Urchin", "description": "You grew up on the streets, learning to survive by your wits. +1 to Dexterity, knowledge of criminal networks, and better prices from shady merchants."},
                    {"id": "noble", "name": "Noble", "description": "Born to privilege, you've had the best education but little real-world experience. +1 to Intelligence, access to high society, and better prices from reputable merchants."},
                    {"id": "soldier", "name": "Soldier", "description": "You've served in the military, trained in discipline and combat. +1 to Strength, better relations with authorities, and occasional combat advantage against military foes."},
                    {"id": "scholar", "name": "Scholar", "description": "You've spent years studying arcane knowledge in prestigious academies. +1 to Intelligence, deeper understanding of magical phenomena, and access to rare scholarly texts."}
                ]
            
            # Display character summary section at the top
            self._render_character_summary(content_x, adjusted_y + 30, content_width)
            
            # Variable to track position for drawing
            y_pos = adjusted_y + 140
            bg_spacing = 20
            card_width = content_width - 40
            card_height = 100
            
            # Calculate total content height for scrolling
            total_content_height = 140 + (len(self.background_options) * (card_height + bg_spacing)) + 50
            self.max_scroll = max(0, total_content_height - self.ui_regions["main_content"].height)
            
            # Draw background options
            for i, background in enumerate(self.background_options):
                # Calculate position with scrolling
                card_y = y_pos + i * (card_height + bg_spacing)
                
                # Skip if outside the visible area
                if (card_y + card_height < content_y or 
                    card_y > content_y + content_height):
                    continue
                
                # Background card (highlight if selected)
                if isinstance(self.character_data["background"], dict) and "id" in self.character_data["background"]:
                    is_selected = self.character_data["background"]["id"] == background["id"]
                else:
                    is_selected = self.character_data["background"] == background["id"]
                    
                card_bg_color = (50, 50, 90, 200) if is_selected else (40, 40, 60, 150)
                
                # Draw card background
                self.ui_renderer.draw_rectangle(
                    content_x, card_y,
                    card_width, card_height,
                    card_bg_color
                )
                
                # Store background rect for click detection (using unadjusted y position)
                bg_rect_y = content_y + 140 + i * (card_height + bg_spacing)
                background["rect"] = pygame.Rect(content_x, bg_rect_y, card_width, card_height)
                
                # Draw border if selected
                if is_selected:
                    # Top border
                    self.ui_renderer.draw_rectangle(
                        content_x, card_y,
                        card_width, 2,
                        (100, 150, 200, 255)
                    )
                    # Bottom border
                    self.ui_renderer.draw_rectangle(
                        content_x, card_y + card_height - 2,
                        card_width, 2,
                        (100, 150, 200, 255)
                    )
                    # Left border
                    self.ui_renderer.draw_rectangle(
                        content_x, card_y,
                        2, card_height,
                        (100, 150, 200, 255)
                    )
                    # Right border
                    self.ui_renderer.draw_rectangle(
                        content_x + card_width - 2, card_y,
                        2, card_height,
                        (100, 150, 200, 255)
                    )
                
                # Draw background name
                self.ui_renderer.render_text(
                    background["name"],
                    self.text_font,
                    (220, 220, 255, 255),
                    content_x + 15, card_y + 15
                )
                
                # Draw background description
                description_lines = self._wrap_text(
                    background["description"],
                    self.small_font,
                    card_width - 30
                )
                
                for j, line in enumerate(description_lines):
                    self.ui_renderer.render_text(
                        line,
                        self.small_font,
                        (200, 200, 200, 220),
                        content_x + 15, card_y + 45 + j * 20
                    )
                
                # Draw "Select" button
                select_btn_width = 80
                select_btn_height = 30
                select_btn_x = content_x + card_width - select_btn_width - 15
                select_btn_y = card_y + card_height - select_btn_height - 15
                
                # Button color (blue if not selected, green if selected)
                select_btn_color = (100, 180, 100, 200) if is_selected else (100, 120, 180, 200)
                
                # Draw button
                self.ui_renderer.draw_rectangle(
                    select_btn_x, select_btn_y,
                    select_btn_width, select_btn_height,
                    select_btn_color
                )
                
                # Store select button rect for click detection (using unadjusted y position)
                select_btn_real_y = content_y + 140 + i * (card_height + bg_spacing) + card_height - select_btn_height - 15
                background["select_rect"] = pygame.Rect(select_btn_x, select_btn_real_y, select_btn_width, select_btn_height)
                
                # Draw button text
                btn_text = "Selected" if is_selected else "Select"
                self.ui_renderer.render_text(
                    btn_text,
                    self.small_font,
                    (220, 220, 255, 255),
                    select_btn_x + 15, select_btn_y + 8
                )
            
            # Add a note about backgrounds
            note_y = y_pos + len(self.background_options) * (card_height + bg_spacing) + 15
            if note_y > content_y - self.scroll_offset and note_y < content_y + content_height - self.scroll_offset:
                self.ui_renderer.render_text(
                    "Note: Your background will influence dialogue options and some quest opportunities.",
                    self.small_font,
                    (180, 180, 200, 200),
                    content_x, note_y
                )
        else:
            # PyGame fallback rendering
            title_surface = self.heading_font.render("Character Background", True, (220, 220, 255))
            screen.blit(title_surface, (content_x, content_y - 30))
            
            # Instructions
            instruction_surface = self.small_font.render(
                "Choose a background story for your character.", 
                True, 
                (200, 200, 220)
            )
            screen.blit(instruction_surface, (content_x, content_y))
        
    def _render_character_summary(self, x, y, width):
        """Render a summary of character information."""
        # Draw a header
        self.ui_renderer.render_text(
            "Character Info",
            self.text_font,
            (220, 220, 255, 255),
            x + 10, y - 20
        )
        
        # Draw background panel
        self.ui_renderer.draw_rectangle(
            x, y,
            width - 40, 80,
            (40, 40, 60, 100)
        )
        
        # Calculate column positions
        col1_x = x + 20
        col2_x = x + width // 2
        row1_y = y + 15
        row2_y = y + 45
        
        # Draw character information in a 2x2 grid
        # Column 1, Row 1
        self.ui_renderer.render_text(
            f"Name: {self.character_data['name']}",
            self.small_font,
            (220, 220, 220, 255),
            col1_x, row1_y
        )
        
        # Column 2, Row 1
        if self.character_data["class"] is not None:
            class_name = self.character_data["class"]["name"] if isinstance(self.character_data["class"], dict) and "name" in self.character_data["class"] else str(self.character_data["class"])
        else:
            class_name = "None"
            
        self.ui_renderer.render_text(
            f"Class: {class_name}",
            self.small_font,
            (220, 220, 220, 255),
            col2_x, row1_y
        )
        
        # Column 1, Row 2
        self.ui_renderer.render_text(
            f"Gender: {self.character_data['gender'].capitalize()}",
            self.small_font,
            (220, 220, 220, 255),
            col1_x, row2_y
        )
        
        # Column 2, Row 2
        bg_text = "Background: "
        if "background" in self.character_data and self.character_data["background"]:
            bg_text += self.character_data["background"]["name"] if isinstance(self.character_data["background"], dict) and "name" in self.character_data["background"] else str(self.character_data["background"])
        else:
            bg_text += "None"
            
        self.ui_renderer.render_text(
            bg_text,
            self.small_font,
            (220, 220, 220, 255),
            col2_x, row2_y
        )

    def _handle_appearance_input(self, event):
        """Handle input for appearance tab."""
        # Check for mouse click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            # Check if we're clicking on an appearance option
            for option in self.appearance_options:
                # Check for left/right arrow clicks
                if "left_rect" in option and option["left_rect"].collidepoint(event.pos):
                    # Find the current index
                    current_value = option["get"]()
                    values = option["values"]
                    
                    # Get index of current value
                    if isinstance(current_value, str):
                        try:
                            current_index = values.index(current_value)
                        except ValueError:
                            current_index = 0
                    else:
                        current_index = current_value if 0 <= current_value < len(values) else 0
                    
                    # Decrease index (wrap around to end if at beginning)
                    new_index = (current_index - 1) % len(values)
                    new_value = values[new_index]
                    
                    # Set the new value
                    option["set"](new_value)
                    
                    # Update the preview character
                    self._update_preview_character()
                    return True
                    
                elif "right_rect" in option and option["right_rect"].collidepoint(event.pos):
                    # Find the current index
                    current_value = option["get"]()
                    values = option["values"]
                    
                    # Get index of current value
                    if isinstance(current_value, str):
                        try:
                            current_index = values.index(current_value)
                        except ValueError:
                            current_index = 0
                    else:
                        current_index = current_value if 0 <= current_value < len(values) else 0
                    
                    # Increase index (wrap around to beginning if at end)
                    new_index = (current_index + 1) % len(values)
                    new_value = values[new_index]
                    
                    # Set the new value
                    option["set"](new_value)
                    
                    # Update the preview character
                    self._update_preview_character()
                    return True
        
        # Check for keyboard input
        elif event.type == pygame.KEYDOWN:
            # If we have an option selected
            if hasattr(self, 'selected_option') and 0 <= self.selected_option < len(self.appearance_options):
                option = self.appearance_options[self.selected_option]
                
                # Handle left/right arrow keys
                if event.key == pygame.K_LEFT:
                    # Same logic as above for decreasing value
                    current_value = option["get"]()
                    values = option["values"]
                    
                    if isinstance(current_value, str):
                        try:
                            current_index = values.index(current_value)
                        except ValueError:
                            current_index = 0
                    else:
                        current_index = current_value if 0 <= current_value < len(values) else 0
                    
                    new_index = (current_index - 1) % len(values)
                    new_value = values[new_index]
                    
                    option["set"](new_value)
                    self._update_preview_character()
                    return True
                    
                elif event.key == pygame.K_RIGHT:
                    # Same logic as above for increasing value
                    current_value = option["get"]()
                    values = option["values"]
                    
                    if isinstance(current_value, str):
                        try:
                            current_index = values.index(current_value)
                        except ValueError:
                            current_index = 0
                    else:
                        current_index = current_value if 0 <= current_value < len(values) else 0
                    
                    new_index = (current_index + 1) % len(values)
                    new_value = values[new_index]
                    
                    option["set"](new_value)
                    self._update_preview_character()
                    return True
                
                # Handle up/down keys for selection
                elif event.key == pygame.K_UP:
                    self.selected_option = max(0, self.selected_option - 1)
                    return True
                elif event.key == pygame.K_DOWN:
                    self.selected_option = min(len(self.appearance_options) - 1, self.selected_option + 1)
                    return True
        
        return False

    def _handle_class_input(self, event):
        """Handle input for class selection step."""
        # Check for mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            mouse_pos = event.pos
            
            # Check for clicks on class options
            for cls in self.available_classes:
                if "rect" in cls and cls["rect"].collidepoint(mouse_pos):
                    # Set the selected class
                    print(f"Selected class: {cls['id']}")
                    self.character_data["class"] = cls  # Store the entire class dictionary
                    # Update abilities when class changes
                    self._update_abilities_for_class()
                    return True
                    
                # Check for select button clicks
                if "select_rect" in cls and cls["select_rect"].collidepoint(mouse_pos):
                    # Set the selected class
                    print(f"Selected class: {cls['id']}")
                    self.character_data["class"] = cls  # Store the entire class dictionary
                    # Update abilities when class changes
                    self._update_abilities_for_class()
                    return True
        
        # Check for keyboard navigation
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                # Select previous class
                if not self.available_classes:
                    return False
                    
                current_index = -1
                for i, cls in enumerate(self.available_classes):
                    if cls["id"] == self.character_data["class"]["id"]:
                        current_index = i
                        break
                        
                if current_index >= 0:
                    new_index = (current_index - 1) % len(self.available_classes)
                    self.character_data["class"] = self.available_classes[new_index]
                    self._update_abilities_for_class()
                    return True
                    
            elif event.key == pygame.K_DOWN:
                # Select next class
                if not self.available_classes:
                    return False
                    
                current_index = -1
                for i, cls in enumerate(self.available_classes):
                    if cls["id"] == self.character_data["class"]["id"]:
                        current_index = i
                        break
                        
                if current_index >= 0:
                    new_index = (current_index + 1) % len(self.available_classes)
                    self.character_data["class"] = self.available_classes[new_index]
                    self._update_abilities_for_class()
                    return True
                    
            elif event.key == pygame.K_RETURN:
                # Confirm current class and proceed
                if self.character_data["class"]:
                    self._go_to_next_step()
                    return True
        
        return False

    def _handle_abilities_input(self, event):
        """Handle input for abilities tab."""
        # Check for mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            mouse_pos = event.pos
            
            # Check for ability selection
            for ability in self.ability_options:
                if "rect" in ability and ability["rect"].collidepoint(mouse_pos):
                    # Toggle ability selection
                    ability_id = ability["id"]
                    if ability_id in self.character_data["abilities"]:
                        self.character_data["abilities"].remove(ability_id)
                    else:
                        # Check if we have reached the maximum number of abilities
                        max_abilities = 3  # Default max
                        if self.character_data["class"] and "max_abilities" in self.character_data["class"]:
                            max_abilities = self.character_data["class"]["max_abilities"]
                            
                        if len(self.character_data["abilities"]) < max_abilities:
                            self.character_data["abilities"].append(ability_id)
                    return True
        
        # Check for keyboard navigation
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                # Select previous ability
                self.selected_option = max(0, self.selected_option - 1)
                return True
                
            elif event.key == pygame.K_DOWN:
                # Select next ability
                self.selected_option = min(len(self.ability_options) - 1, self.selected_option + 1)
                return True
                
            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                # Toggle selected ability
                if 0 <= self.selected_option < len(self.ability_options):
                    ability = self.ability_options[self.selected_option]
                    ability_id = ability["id"]
                    
                    if ability_id in self.character_data["abilities"]:
                        self.character_data["abilities"].remove(ability_id)
                    else:
                        # Check if we have reached the maximum number of abilities
                        max_abilities = 3  # Default max
                        if self.character_data["class"] and "max_abilities" in self.character_data["class"]:
                            max_abilities = self.character_data["class"]["max_abilities"]
                            
                        if len(self.character_data["abilities"]) < max_abilities:
                            self.character_data["abilities"].append(ability_id)
                    return True
        
        return False

    def _render_name_tab(self, screen, content_x, content_y):
        """Render the character name input tab."""
        # Get content area height
        content_height = self.ui_regions["main_content"].height
        
        # Draw name input field
        input_field_width = 400
        input_field_height = 50
        input_field_x = content_x + (self.ui_regions["main_content"].width - input_field_width) // 2
        input_field_y = content_y + 100 - self.scroll_offset
        
        # Draw input field background
        pygame.draw.rect(screen, (40, 40, 60), 
                         (input_field_x, input_field_y, input_field_width, input_field_height), 
                         border_radius=5)
        pygame.draw.rect(screen, (70, 70, 100), 
                         (input_field_x, input_field_y, input_field_width, input_field_height), 
                         width=2, border_radius=5)
        
        # Draw label
        label = self.heading_font.render("Character Name:", True, (220, 220, 255))
        screen.blit(label, (input_field_x, input_field_y - 40))
        
        # Draw character name
        current_name = self.character_data["name"]
        name_surface = self.heading_font.render(current_name, True, (255, 255, 255))
        name_x = input_field_x + 15
        name_y = input_field_y + (input_field_height - name_surface.get_height()) // 2
        screen.blit(name_surface, (name_x, name_y))
        
        # Draw cursor (if active)
        if self.name_input_active and self.name_input_cursor_visible:
            cursor_x = name_x + name_surface.get_width() + 2
            cursor_y = name_y
            cursor_height = name_surface.get_height()
            pygame.draw.line(screen, (255, 255, 255), 
                             (cursor_x, cursor_y), 
                             (cursor_x, cursor_y + cursor_height), 
                             width=2)
        
        # Draw "Random Name" button
        button_width = 200
        button_height = 40
        button_x = input_field_x + (input_field_width - button_width) // 2
        button_y = input_field_y + input_field_height + 30
        
        # Store button rect for clicking
        self.random_name_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Draw button with hover effect
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.random_name_button_rect.collidepoint(mouse_pos)
        button_color = (80, 100, 160) if is_hovered else (60, 80, 140)
        
        pygame.draw.rect(screen, button_color, self.random_name_button_rect, border_radius=5)
        pygame.draw.rect(screen, (100, 120, 180), self.random_name_button_rect, width=2, border_radius=5)
        
        # Draw button text
        button_text = self.text_font.render("Random Name", True, (255, 255, 255))
        button_text_x = button_x + (button_width - button_text.get_width()) // 2
        button_text_y = button_y + (button_height - button_text.get_height()) // 2
        screen.blit(button_text, (button_text_x, button_text_y))
        
        # Draw character summary
        summary_y = button_y + button_height + 50
        self._render_character_summary(input_field_x, summary_y, input_field_width)

    def _generate_random_name(self):
        """Generate a random name based on the character's gender."""
        gender = self.character_data["gender"]
        import random
        
        # Generate a random name from the corresponding gender list
        if gender in self.random_names:
            name_list = self.random_names[gender]
            random_name = random.choice(name_list)
            self.character_data["name"] = random_name

    def _switch_to_tab_index(self, index):
        """
        Switch to a specific tab by index.
        
        Args:
            index: The zero-based index of the tab to switch to.
        """
        if self.tab_buttons and 0 <= index < len(self.tab_buttons):
            # Update the active tab
            for i, tab in enumerate(self.tab_buttons):
                tab["active"] = (i == index)
            
            # Set the active tab value
            self.active_tab = self.tab_buttons[index]["value"]
            print(f"Switched to tab: {self.active_tab}")
            
            # Update the current step to match the selected tab
            # This ensures the correct content is rendered
            if self.active_tab == "name":
                self.current_step = "name"
            elif self.active_tab == "appearance":
                self.current_step = "appearance"
            elif self.active_tab == "attributes":
                self.current_step = "attributes"
            elif self.active_tab == "abilities":
                self.current_step = "abilities"
            elif self.active_tab == "background":
                self.current_step = "background"
            
            # Reset scroll position when switching tabs
            self.scroll_offset = 0
            
            # Update the selected option
            self.selected_option = 0
