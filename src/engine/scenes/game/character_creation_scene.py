# src/engine/scenes/game/character_creation_scene.py

import pygame
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Callable
import os

from ..scene import Scene
from ...combat.character_classes import CharacterClass
from ...ecs.world import World
from ...ecs.components import Transform, Sprite
import pygame.font

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
        
        # Callback when character creation is complete
        self.on_character_created = on_character_created
        
        # Character creation state
        self.current_step = "class"  # class, appearance, attributes, background, name, equipment, summary
        self.character_data = {
            "name": "Hero",
            "gender": "male",  # male/female
            "class": "warrior",  # warrior/mage/rogue
            "appearance": {
                "skin_tone": 0,  # 0-3 (pale to dark)
                "hair_style": 0,  # 0-5 (different styles)
                "hair_color": 0,  # 0-5 (blonde, brown, black, red, etc.)
                "face_style": 0,  # 0-3 (different face shapes/features)
                "body_type": 0,   # 0-2 (average, muscular, thin)
            },
            "attributes": {
                "strength": 10,
                "dexterity": 10,
                "intelligence": 10,
                "vitality": 10,
                "charisma": 10
            },
            "abilities": []
        }
        
        # Input state
        self.active_tab = "appearance"  # appearance/attributes/abilities
        self.selected_option = 0
        self.input_cooldown = 0
        
        # Character preview components
        self.preview_surface = None
        self.character_sprite = None
        self.hd2d_renderer = None
        self.procedural_generator = None
        
        # Background
        self.background = None
        
        # Whether assets have been generated
        self.assets_generated = False
        
        # Fonts
        self.title_font = None
        self.option_font = None
        self.desc_font = None
        
        # Available character classes
        self.available_classes = []
        
        # Available backgrounds
        self.available_backgrounds = []
        
        # UI elements
        self.title_font = None
        self.text_font = None
        self.buttons = []
        self.active_ui_elements = []
        
        # Preview character entity
        self.preview_entity_id = None
        
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
        """Load available character classes."""
        # In a real implementation, these would be loaded from data files
        # For now, we'll create some placeholder classes
        self.available_classes = [
            {"id": "warrior", "name": "Warrior", "description": "A strong melee fighter skilled with weapons and armor."},
            {"id": "mage", "name": "Mage", "description": "A wielder of arcane magic, capable of devastating spells."},
            {"id": "rogue", "name": "Rogue", "description": "A stealthy character specializing in sneak attacks and traps."},
            {"id": "cleric", "name": "Cleric", "description": "A divine spellcaster with healing and support abilities."}
        ]
        
    def _load_backgrounds(self):
        """Load available character backgrounds."""
        # These would also be loaded from data files in a real implementation
        self.available_backgrounds = [
            {"id": "noble", "name": "Noble", "description": "Born to privilege, you have connections and wealth."},
            {"id": "orphan", "name": "Orphan", "description": "Raised on the streets, you've learned to survive by any means."},
            {"id": "soldier", "name": "Soldier", "description": "Trained in military discipline and combat tactics."},
            {"id": "scholar", "name": "Scholar", "description": "Educated in ancient lore and magical theory."}
        ]
        
    def _init_ui(self):
        """Initialize UI elements for character creation."""
        # Create fonts
        self.title_font = pygame.font.SysFont(None, 48)
        self.text_font = pygame.font.SysFont(None, 24)
        self.option_font = pygame.font.SysFont(None, 24)
        self.desc_font = pygame.font.SysFont(None, 20)
        
        # Create preview surface for character rendering
        self.preview_surface = pygame.Surface((300, 400))
        self.preview_surface.fill((40, 40, 60))  # Dark background
        
        # Create buttons and UI elements
        # These would be created based on the current step
        
        # Tab buttons
        self.tab_buttons = [
            {"text": "Appearance", "value": "appearance", "rect": pygame.Rect(100, 100, 150, 40)},
            {"text": "Attributes", "value": "attributes", "rect": pygame.Rect(260, 100, 150, 40)},
            {"text": "Abilities", "value": "abilities", "rect": pygame.Rect(420, 100, 150, 40)}
        ]
        
        # Options for each tab
        self.appearance_options = [
            {"text": "Gender", "property": "gender", "values": ["male", "female"], "get": lambda: self.character_data["gender"], "set": lambda v: self._set_character_property("gender", v)},
            {"text": "Skin Tone", "property": "skin_tone", "values": ["pale", "light", "tan", "dark"], "get": lambda: self.character_data["appearance"]["skin_tone"], "set": lambda v: self._set_appearance_property("skin_tone", v)},
            {"text": "Hair Style", "property": "hair_style", "values": ["style1", "style2", "style3", "style4", "style5", "style6"], "get": lambda: self.character_data["appearance"]["hair_style"], "set": lambda v: self._set_appearance_property("hair_style", v)},
            {"text": "Hair Color", "property": "hair_color", "values": ["blonde", "light brown", "dark brown", "black", "red", "white"], "get": lambda: self.character_data["appearance"]["hair_color"], "set": lambda v: self._set_appearance_property("hair_color", v)},
            {"text": "Face Style", "property": "face_style", "values": ["face1", "face2", "face3", "face4"], "get": lambda: self.character_data["appearance"]["face_style"], "set": lambda v: self._set_appearance_property("face_style", v)},
            {"text": "Body Type", "property": "body_type", "values": ["average", "muscular", "thin"], "get": lambda: self.character_data["appearance"]["body_type"], "set": lambda v: self._set_appearance_property("body_type", v)}
        ]
        
        self.attribute_options = [
            {"text": "Strength", "property": "strength", "min": 5, "max": 20, "get": lambda: self.character_data["attributes"]["strength"], "set": lambda v: self._set_attribute_property("strength", v)},
            {"text": "Dexterity", "property": "dexterity", "min": 5, "max": 20, "get": lambda: self.character_data["attributes"]["dexterity"], "set": lambda v: self._set_attribute_property("dexterity", v)},
            {"text": "Intelligence", "property": "intelligence", "min": 5, "max": 20, "get": lambda: self.character_data["attributes"]["intelligence"], "set": lambda v: self._set_attribute_property("intelligence", v)},
            {"text": "Vitality", "property": "vitality", "min": 5, "max": 20, "get": lambda: self.character_data["attributes"]["vitality"], "set": lambda v: self._set_attribute_property("vitality", v)},
            {"text": "Charisma", "property": "charisma", "min": 5, "max": 20, "get": lambda: self.character_data["attributes"]["charisma"], "set": lambda v: self._set_attribute_property("charisma", v)}
        ]
        
        self.ability_options = [
            {"text": "Class", "property": "class", "values": ["warrior", "mage", "rogue"], "get": lambda: self.character_data["class"], "set": lambda v: self._set_character_property("class", v)}
        ]
        
        # Control buttons
        self.control_buttons = [
            {"text": "Cancel", "action": self._cancel_creation, "rect": pygame.Rect(200, 500, 100, 40)},
            {"text": "Create Character", "action": self._create_character, "rect": pygame.Rect(400, 500, 200, 40)}
        ]
        
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
        
        # Create name input field and random name button
        
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
        
        # Clear screen (this would be handled by the renderer in real implementation)
        screen.fill((20, 20, 40))  # Dark blue background
        
        # Render background
        self._render_background(screen)
        
        # Render preview character
        self._render_preview_character(screen)
        
        # Render UI elements based on current step
        self._render_ui(screen)
        
    def _render_background(self, screen):
        """Render scene background."""
        # In a real implementation, this would render a background image or effect
        # For now, just draw a simple gradient background
        height = screen.get_height()
        for y in range(0, height, 2):  # Skip every other line for efficiency
            color_value = int(20 + (y / height) * 40)  # Gradient from dark to slightly lighter
            color = (color_value, color_value, color_value + 20)  # Bluish tint
            pygame.draw.line(screen, color, (0, y), (screen.get_width(), y))
        
    def _render_preview_character(self, screen):
        """Render preview character."""
        # Normally, the world renderer would handle this
        # For now, just draw a simple placeholder
        pygame.draw.circle(screen, (255, 200, 150), 
                          (screen.get_width() // 2, screen.get_height() // 2), 
                          50)  # Head
        pygame.draw.rect(screen, (100, 100, 150), 
                         (screen.get_width() // 2 - 40, 
                          screen.get_height() // 2 + 50, 
                          80, 100))  # Body
        
    def _render_ui(self, screen):
        """Render UI elements."""
        # Render title
        title_text = f"Character Creation - {self._get_step_title()}"
        title_surface = self.title_font.render(title_text, True, (255, 255, 255))
        screen.blit(title_surface, (20, 20))
        
        # Render step info based on current step
        self._render_step_ui(screen)
        
        # Render navigation buttons
        self._render_navigation_buttons(screen)
        
        # Render character data
        self._render_character_data(screen)
        
    def _render_step_ui(self, screen):
        """Render UI elements specific to the current step."""
        if self.current_step == "class":
            # Render class options
            self._render_class_options(screen)
        elif self.current_step == "appearance":
            # Render appearance options
            self._render_appearance_options(screen)
        elif self.current_step == "attributes":
            # Render attribute options
            self._render_attribute_options(screen)
        elif self.current_step == "background":
            # Render background options
            self._render_background_options(screen)
        elif self.current_step == "name":
            # Render name input
            self._render_name_input(screen)
        elif self.current_step == "equipment":
            # Render equipment options
            self._render_equipment_options(screen)
        elif self.current_step == "summary":
            # Render character summary
            self._render_character_summary(screen)
            
    def _render_class_options(self, screen):
        """Render class selection options."""
        # This would display the available classes with descriptions
        y = 100
        for cls in self.available_classes:
            # Highlight selected class
            color = (255, 255, 0) if self.character_data["class"] and cls["id"] == self.character_data["class"]["id"] else (255, 255, 255)
            text = f"{cls['name']}: {cls['description']}"
            text_surface = self.text_font.render(text, True, color)
            screen.blit(text_surface, (50, y))
            y += 40
            
    def _render_appearance_options(self, screen):
        """Render appearance customization options."""
        # This would display appearance options
        # (body type, face, hair, etc.)
        text = "Appearance Customization"
        text_surface = self.text_font.render(text, True, (255, 255, 255))
        screen.blit(text_surface, (50, 100))
        
    def _render_attribute_options(self, screen):
        """Render attribute distribution options."""
        # This would display attribute sliders/controls
        y = 100
        for attr, value in self.character_data["attributes"].items():
            text = f"{attr.capitalize()}: {value}"
            text_surface = self.text_font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (50, y))
            y += 30
            
    def _render_background_options(self, screen):
        """Render background selection options."""
        # This would display the available backgrounds with descriptions
        y = 100
        for bg in self.available_backgrounds:
            # Highlight selected background
            color = (255, 255, 0) if self.character_data["background"] and bg["id"] == self.character_data["background"]["id"] else (255, 255, 255)
            text = f"{bg['name']}: {bg['description']}"
            text_surface = self.text_font.render(text, True, color)
            screen.blit(text_surface, (50, y))
            y += 40
            
    def _render_name_input(self, screen):
        """Render name input field."""
        # This would display a text input field
        text = f"Name: {self.character_data['name']}"
        text_surface = self.text_font.render(text, True, (255, 255, 255))
        screen.blit(text_surface, (50, 100))
        
        # Draw a text input box
        pygame.draw.rect(screen, (80, 80, 80), (50, 130, 300, 40))
        pygame.draw.rect(screen, (150, 150, 150), (50, 130, 300, 40), 2)
        
        # Display current name in the box
        name_surface = self.text_font.render(self.character_data["name"], True, (255, 255, 255))
        screen.blit(name_surface, (60, 140))
        
    def _render_equipment_options(self, screen):
        """Render equipment selection options."""
        # This would display equipment options based on class and background
        text = "Equipment Selection"
        text_surface = self.text_font.render(text, True, (255, 255, 255))
        screen.blit(text_surface, (50, 100))
        
    def _render_character_summary(self, screen):
        """Render character summary."""
        # This would display a summary of all character choices
        y = 100
        
        # Class and background
        class_text = f"Class: {self.character_data['class']['name']}"
        text_surface = self.text_font.render(class_text, True, (255, 255, 255))
        screen.blit(text_surface, (50, y))
        y += 30
        
        bg_text = f"Background: {self.character_data['background']['name']}"
        text_surface = self.text_font.render(bg_text, True, (255, 255, 255))
        screen.blit(text_surface, (50, y))
        y += 30
        
        # Name
        name_text = f"Name: {self.character_data['name']}"
        text_surface = self.text_font.render(name_text, True, (255, 255, 255))
        screen.blit(text_surface, (50, y))
        y += 30
        
        # Attributes
        attr_text = "Attributes:"
        text_surface = self.text_font.render(attr_text, True, (255, 255, 255))
        screen.blit(text_surface, (50, y))
        y += 30
        
        # Display attributes
        for attr, value in self.character_data["attributes"].items():
            text = f"  {attr.capitalize()}: {value}"
            text_surface = self.text_font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (50, y))
            y += 20
            
        # Confirmation instructions
        y += 20
        confirm_text = "Press ENTER to confirm character creation"
        text_surface = self.text_font.render(confirm_text, True, (255, 255, 0))
        screen.blit(text_surface, (50, y))
        
    def _render_navigation_buttons(self, screen):
        """Render navigation buttons (previous, next)."""
        # Previous button
        if self.current_step != "class":
            prev_text = "< Previous"
            text_surface = self.text_font.render(prev_text, True, (200, 200, 255))
            screen.blit(text_surface, (50, self.renderer.height - 50))
            
        # Next button
        if self.current_step != "summary":
            next_text = "Next >"
            text_surface = self.text_font.render(next_text, True, (200, 200, 255))
            text_width = text_surface.get_width()
            screen.blit(text_surface, (self.renderer.width - 50 - text_width, self.renderer.height - 50))
            
    def _render_character_data(self, screen):
        """Render current character data (sidebar)."""
        # Display current selections in a sidebar
        sidebar_x = self.renderer.width - 250
        sidebar_y = 80
        sidebar_width = 230
        sidebar_height = 300
        
        # Draw sidebar background
        pygame.draw.rect(screen, (0, 0, 0, 128), (sidebar_x, sidebar_y, sidebar_width, sidebar_height))
        pygame.draw.rect(screen, (100, 100, 150), (sidebar_x, sidebar_y, sidebar_width, sidebar_height), 2)
        
        # Draw sidebar title
        sidebar_title = "Character"
        title_surface = self.text_font.render(sidebar_title, True, (255, 255, 200))
        screen.blit(title_surface, (sidebar_x + 10, sidebar_y + 10))
        
        # Draw character info
        y = sidebar_y + 40
        
        # Name
        name_text = f"Name: {self.character_data['name']}"
        text_surface = self.text_font.render(name_text, True, (255, 255, 255))
        screen.blit(text_surface, (sidebar_x + 10, y))
        y += 25
        
        # Class
        if self.character_data["class"]:
            class_text = f"Class: {self.character_data['class']['name']}"
            text_surface = self.text_font.render(class_text, True, (255, 255, 255))
            screen.blit(text_surface, (sidebar_x + 10, y))
        y += 25
        
        # Background
        if self.character_data["background"]:
            bg_text = f"Background: {self.character_data['background']['name']}"
            text_surface = self.text_font.render(bg_text, True, (255, 255, 255))
            screen.blit(text_surface, (sidebar_x + 10, y))
            
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
        
    def handle_event(self, event):
        """
        Handle input events.
        
        Args:
            event: The pygame event to handle.
        """
        # Handle navigation buttons
        if self._handle_navigation_input(event):
            return True
            
        # Handle step-specific input
        if self.current_step == "class":
            return self._handle_class_selection_input(event)
        elif self.current_step == "appearance":
            return self._handle_appearance_input(event)
        elif self.current_step == "attributes":
            return self._handle_attributes_input(event)
        elif self.current_step == "background":
            return self._handle_background_input(event)
        elif self.current_step == "name":
            return self._handle_name_input(event)
        elif self.current_step == "equipment":
            return self._handle_equipment_input(event)
        elif self.current_step == "summary":
            return self._handle_summary_input(event)
            
        return False
        
    def _handle_navigation_input(self, event):
        """Handle navigation button input."""
        if event.type == pygame.KEYDOWN:
            # Previous step
            if event.key == pygame.K_LEFT:
                self._go_to_previous_step()
                return True
                
            # Next step
            elif event.key == pygame.K_RIGHT:
                self._go_to_next_step()
                return True
                
        return False
        
    def _go_to_previous_step(self):
        """Go to the previous character creation step."""
        if self.current_step == "appearance":
            self._setup_class_selection()
        elif self.current_step == "attributes":
            self._setup_appearance_customization()
        elif self.current_step == "background":
            self._setup_attribute_distribution()
        elif self.current_step == "name":
            self._setup_background_selection()
        elif self.current_step == "equipment":
            self._setup_name_selection()
        elif self.current_step == "summary":
            self._setup_equipment_selection()
            
    def _go_to_next_step(self):
        """Go to the next character creation step."""
        if self.current_step == "class":
            self._setup_appearance_customization()
        elif self.current_step == "appearance":
            self._setup_attribute_distribution()
        elif self.current_step == "attributes":
            self._setup_background_selection()
        elif self.current_step == "background":
            self._setup_name_selection()
        elif self.current_step == "name":
            self._setup_equipment_selection()
        elif self.current_step == "equipment":
            self._setup_summary()
        elif self.current_step == "summary":
            self._complete_character_creation()
            
    def _handle_class_selection_input(self, event):
        """Handle input for class selection step."""
        # In a real implementation, this would handle class selection buttons
        return False
        
    def _handle_appearance_input(self, event):
        """Handle input for appearance customization step."""
        # In a real implementation, this would handle appearance customization controls
        return False
        
    def _handle_attributes_input(self, event):
        """Handle input for attribute distribution step."""
        # In a real implementation, this would handle attribute adjustment controls
        return False
        
    def _handle_background_input(self, event):
        """Handle input for background selection step."""
        # In a real implementation, this would handle background selection buttons
        return False
        
    def _handle_name_input(self, event):
        """Handle input for name selection step."""
        # In a real implementation, this would handle name input field
        if event.type == pygame.KEYDOWN:
            # Handle text input for name
            if event.key == pygame.K_BACKSPACE:
                # Remove last character
                self.character_data["name"] = self.character_data["name"][:-1]
                return True
            elif event.unicode.isalpha() or event.unicode.isspace():
                # Add character to name (only allow letters and spaces)
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
        """Complete character creation and call the callback."""
        print("Character creation complete!")
        print(f"Created character: {self.character_data['name']}, {self.character_data['class']['name']}")
        
        # Create the actual player character entity based on selections
        # This would typically be done by the game scene or a character factory
        
        # Call the callback if provided
        if self.on_character_created:
            self.on_character_created(self.character_data)
            
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
        # Draw a simple character silhouette
        color = (150, 150, 150)  # Gray silhouette
        
        # Body
        pygame.draw.ellipse(self.preview_surface, color, (125, 100, 50, 80))  # Head
        pygame.draw.rect(self.preview_surface, color, (135, 180, 30, 100))    # Torso
        pygame.draw.rect(self.preview_surface, color, (125, 280, 20, 80))     # Left leg
        pygame.draw.rect(self.preview_surface, color, (155, 280, 20, 80))     # Right leg
        pygame.draw.rect(self.preview_surface, color, (105, 190, 20, 80))     # Left arm
        pygame.draw.rect(self.preview_surface, color, (175, 190, 20, 80))     # Right arm
        
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
        return []
        
    def _cancel_creation(self):
        """Cancel character creation and return to main menu."""
        from ...ui.menus.main_menu import MainMenu
        self.manager.engine.menu_manager.push_menu(MainMenu(self.manager))
        
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
            
    def _switch_tab(self):
        """Switch to the next tab."""
        tabs = ["appearance", "attributes", "abilities"]
        current_idx = tabs.index(self.active_tab)
        self.active_tab = tabs[(current_idx + 1) % len(tabs)]
        self.selected_option = 0
        
    def _confirm_selection(self):
        """Confirm current selection or perform action."""
        # Currently used for confirmation buttons
        mouse_pos = pygame.mouse.get_pos()
        
        # Check control buttons
        for button in self.control_buttons:
            if button["rect"].collidepoint(mouse_pos):
                button["action"]()
                return
                
    def render(self, screen=None):
        """Render the character creation scene."""
        screen = screen or self.renderer.screen
        
        # Draw background
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill((40, 40, 60))
            
        # Draw character preview
        if self.preview_surface:
            screen.blit(self.preview_surface, (600, 150))
            
        # Draw title
        title_text = self.title_font.render("Character Creation", True, (220, 220, 220))
        screen.blit(title_text, (50, 50))
        
        # Draw tabs
        for i, tab in enumerate(self.tab_buttons):
            color = (150, 200, 250) if tab["value"] == self.active_tab else (100, 100, 150)
            pygame.draw.rect(screen, color, tab["rect"])
            
            tab_text = self.option_font.render(tab["text"], True, (230, 230, 230))
            text_rect = tab_text.get_rect(center=tab["rect"].center)
            screen.blit(tab_text, text_rect)
            
        # Draw options for current tab
        options = self._get_current_options()
        for i, option in enumerate(options):
            y_pos = 160 + i * 40
            color = (200, 220, 255) if i == self.selected_option else (180, 180, 180)
            
            # Option name
            option_text = self.option_font.render(option["text"], True, color)
            screen.blit(option_text, (100, y_pos))
            
            # Option value
            if "values" in option:
                # For options with predefined values
                value_text = self.option_font.render(str(option["get"]()), True, color)
                screen.blit(value_text, (300, y_pos))
            elif "min" in option and "max" in option:
                # For numeric options
                value = option["get"]()
                value_text = self.option_font.render(str(value), True, color)
                screen.blit(value_text, (300, y_pos))
                
                # Draw a bar for numeric values
                bar_rect = pygame.Rect(350, y_pos + 5, 150, 20)
                pygame.draw.rect(screen, (60, 60, 80), bar_rect)
                
                # Calculate filled portion based on value
                fill_width = int(150 * (value - option["min"]) / (option["max"] - option["min"]))
                fill_rect = pygame.Rect(350, y_pos + 5, fill_width, 20)
                pygame.draw.rect(screen, (100, 180, 255), fill_rect)
                
        # Draw control buttons
        for button in self.control_buttons:
            pygame.draw.rect(screen, (80, 100, 120), button["rect"])
            
            button_text = self.option_font.render(button["text"], True, (230, 230, 230))
            text_rect = button_text.get_rect(center=button["rect"].center)
            screen.blit(button_text, text_rect)
            
    def handle_event(self, event):
        """Handle pygame events for the character creation scene."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check for tab selection
                for tab in self.tab_buttons:
                    if tab["rect"].collidepoint(event.pos):
                        self.active_tab = tab["value"]
                        self.selected_option = 0
                        return True
                        
                # Check for control button clicks
                for button in self.control_buttons:
                    if button["rect"].collidepoint(event.pos):
                        button["action"]()
                        return True
                        
        return super().handle_event(event) 