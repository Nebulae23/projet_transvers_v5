# src/engine/ui/menus/pause_menu.py
import pygame
from typing import Dict, List, Callable

from ..ui_base import UIElement, Button, Panel, Label

class PauseMenu:
    """
    Pause menu for the game.
    Displayed when the game is paused during gameplay.
    """
    def __init__(self, width: int, height: int, on_resume: Callable = None, on_save_game: Callable = None,
                 on_load_game: Callable = None, on_options: Callable = None, on_quit: Callable = None):
        """
        Initialize the pause menu.
        
        Args:
            width (int): Screen width.
            height (int): Screen height.
            on_resume (callable): Callback when 'Resume' is selected.
            on_save_game (callable): Callback when 'Save Game' is selected.
            on_load_game (callable): Callback when 'Load Game' is selected.
            on_options (callable): Callback when 'Options' is selected.
            on_quit (callable): Callback when 'Quit to Main Menu' is selected.
        """
        self.width = width
        self.height = height
        
        # Callbacks
        self.on_resume = on_resume
        self.on_save_game = on_save_game
        self.on_load_game = on_load_game
        self.on_options = on_options
        self.on_quit = on_quit
        
        # UI elements
        self.panel = None
        self.title_label = None
        self.buttons = []
        self.ui_elements = []
        
        # Initialize UI
        self._init_ui()
        
    def _init_ui(self):
        """Initialize UI elements."""
        # Create main panel
        self.panel = Panel(
            x=self.width // 2 - 150,
            y=self.height // 2 - 150,
            width=300,
            height=300,
            color=(20, 20, 30, 230)  # Semi-transparent dark blue
        )
        
        # Create title
        self.title_label = Label(
            x=self.width // 2,
            y=self.height // 2 - 120,
            text="Game Paused",
            font_size=36,
            color=(255, 255, 255),
            centered=True
        )
        
        # Create buttons
        button_width = 200
        button_height = 30
        button_x = self.width // 2 - button_width // 2
        button_spacing = 40
        
        # Resume button
        resume_btn = Button(
            x=button_x,
            y=self.height // 2 - 70,
            width=button_width,
            height=button_height,
            text="Resume",
            on_click=self._on_resume_click
        )
        self.buttons.append(resume_btn)
        
        # Save Game button
        save_game_btn = Button(
            x=button_x,
            y=self.height // 2 - 70 + button_spacing,
            width=button_width,
            height=button_height,
            text="Save Game",
            on_click=self._on_save_game_click
        )
        self.buttons.append(save_game_btn)
        
        # Load Game button
        load_game_btn = Button(
            x=button_x,
            y=self.height // 2 - 70 + 2 * button_spacing,
            width=button_width,
            height=button_height,
            text="Load Game",
            on_click=self._on_load_game_click
        )
        self.buttons.append(load_game_btn)
        
        # Options button
        options_btn = Button(
            x=button_x,
            y=self.height // 2 - 70 + 3 * button_spacing,
            width=button_width,
            height=button_height,
            text="Options",
            on_click=self._on_options_click
        )
        self.buttons.append(options_btn)
        
        # Quit button
        quit_btn = Button(
            x=button_x,
            y=self.height // 2 - 70 + 4 * button_spacing,
            width=button_width,
            height=button_height,
            text="Quit to Main Menu",
            on_click=self._on_quit_click
        )
        self.buttons.append(quit_btn)
        
        # Add all elements to UI elements list
        self.ui_elements = [self.panel, self.title_label] + self.buttons
        
    def update(self, dt):
        """
        Update menu logic.
        
        Args:
            dt (float): Time elapsed since last frame.
        """
        # Update button animations
        for button in self.buttons:
            button.update(dt)
            
    def draw(self, screen):
        """
        Draw the menu.
        
        Args:
            screen: The pygame screen to draw on.
        """
        # Create overlay for darkening the background
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        screen.blit(overlay, (0, 0))
        
        # Draw panel
        self.panel.draw(screen)
        
        # Draw title
        self.title_label.draw(screen)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(screen)
            
    def handle_event(self, event):
        """
        Handle input events.
        
        Args:
            event: The pygame event to handle.
            
        Returns:
            bool: True if event was handled, False otherwise.
        """
        # ESC key to resume game
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.on_resume:
                self.on_resume()
            return True
            
        # Check if any button handled the event
        for button in self.buttons:
            if button.handle_event(event):
                return True
                
        return False
        
    def _on_resume_click(self):
        """Handle Resume button click."""
        print("Resume clicked")
        if self.on_resume:
            self.on_resume()
            
    def _on_save_game_click(self):
        """Handle Save Game button click."""
        print("Save Game clicked")
        if self.on_save_game:
            self.on_save_game()
            
    def _on_load_game_click(self):
        """Handle Load Game button click."""
        print("Load Game clicked")
        if self.on_load_game:
            self.on_load_game()
            
    def _on_options_click(self):
        """Handle Options button click."""
        print("Options clicked")
        if self.on_options:
            self.on_options()
            
    def _on_quit_click(self):
        """Handle Quit button click."""
        print("Quit to Main Menu clicked")
        if self.on_quit:
            self.on_quit()