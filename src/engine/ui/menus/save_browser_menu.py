# src/engine/ui/menus/save_browser_menu.py
import pygame
import os
import json
import datetime
from typing import Callable, Dict, Any, List, Optional
from ..ui_base import Panel, Button, Label

class SaveFile:
    """Represents a save file with metadata."""
    def __init__(self, path: str):
        self.path = path
        self.valid = False
        self.data = {}
        self.name = os.path.basename(path)
        self.timestamp = None
        self.thumbnail = None
        self.character_name = "Unknown"
        self.character_level = 0
        self.character_class = "Unknown"
        self.location = "Unknown"
        self.playtime = "Unknown"
        
        print(f"Loading save file: {path}")
        
        # Try to load and parse the save file
        try:
            with open(path, 'r') as f:
                self.data = json.load(f)
                
            # Get basic save data
            if "timestamp" in self.data:
                try:
                    self.timestamp = datetime.datetime.strptime(
                        self.data["timestamp"], "%Y%m%d_%H%M%S"
                    )
                except ValueError:
                    # Try alternate format
                    filename = os.path.basename(path)
                    date_part = filename.split('_')[1:3]
                    if len(date_part) >= 2:
                        date_str = date_part[0] + '_' + date_part[1]
                        try:
                            self.timestamp = datetime.datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                        except:
                            print(f"  Could not parse timestamp from filename: {filename}")
                print(f"  Timestamp: {self.timestamp}")
            
            # Get character info
            if "player" in self.data:
                player_data = self.data["player"]
                self.character_name = player_data.get("name", "Unknown")
                self.character_level = player_data.get("level", 0)
                self.character_class = player_data.get("class", "Unknown")
                print(f"  Character: {self.character_name}, Level {self.character_level}, Class: {self.character_class}")
            
            # Get world info
            if "world" in self.data:
                world_data = self.data["world"]
                self.location = world_data.get("location", "Unknown")
                print(f"  Location: {self.location}")
                
            # Even if we didn't find all data, mark as valid so we can display something
            self.valid = True
            print(f"  Save file loaded successfully: {self.summary}")
        except Exception as e:
            print(f"Error loading save file {path}: {e}")
            import traceback
            traceback.print_exc()
    
    @property
    def formatted_timestamp(self) -> str:
        """Return a formatted timestamp string."""
        if self.timestamp:
            return self.timestamp.strftime("%d %b %Y %H:%M")
        return "Unknown Date"
    
    @property
    def summary(self) -> str:
        """Return a brief summary of the save."""
        return f"{self.character_name} - Level {self.character_level} {self.character_class}"

class SaveBrowserMenu:
    """Menu for browsing and selecting save files."""
    def __init__(self, width: int, height: int, 
                 on_save_selected: Callable[[Dict[str, Any]], None] = None, 
                 on_cancel: Callable[[], None] = None):
        self.width = width
        self.height = height
        self.on_save_selected = on_save_selected
        self.on_cancel = on_cancel
        
        # UI elements
        self.ui_elements = []
        self.buttons = []
        self.labels = []
        self.save_panels = []
        
        # Save data
        self.saves: List[SaveFile] = []
        self.selected_save: Optional[SaveFile] = None
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Initialize UI
        self._load_saves()
        self._init_ui()
        
    def _load_saves(self):
        """Load available save files."""
        self.saves = []
        
        # Check if saves directory exists
        save_dir = os.path.join(os.getcwd(), "saves")
        print(f"Looking for save files in: {save_dir}")
        
        if not os.path.exists(save_dir):
            print(f"Saves directory not found: {save_dir}")
            return
        
        # List all JSON files in the saves directory
        try:
            all_files = os.listdir(save_dir)
            print(f"Files in saves directory: {all_files}")
            
            for filename in sorted(all_files, reverse=True):
                if filename.endswith(".json"):
                    save_path = os.path.join(save_dir, filename)
                    print(f"Found save file: {save_path}")
                    save_file = SaveFile(save_path)
                    if save_file.valid:
                        self.saves.append(save_file)
                    else:
                        print(f"Save file {save_path} is not valid and will be skipped")
        except Exception as e:
            print(f"Error listing save files: {e}")
        
        print(f"Found {len(self.saves)} valid save files")
        
        # Debug: Print all loaded saves
        for i, save in enumerate(self.saves):
            print(f"Save {i+1}: {save.summary}, Location: {save.location}, Date: {save.formatted_timestamp}")
        
    def _init_ui(self):
        """Initialize UI elements."""
        # Main panel
        panel_width = min(800, self.width - 40)
        panel_height = min(600, self.height - 40)
        panel_x = (self.width - panel_width) // 2
        panel_y = (self.height - panel_height) // 2
        
        # Print coordinates for debugging
        print(f"Initializing SaveBrowserMenu UI with dimensions: {self.width}x{self.height}")
        print(f"Creating main panel at ({panel_x}, {panel_y}) with size {panel_width}x{panel_height}")
        
        self.main_panel = Panel(
            x=panel_x,
            y=panel_y,
            width=panel_width,
            height=panel_height,
            color=(40, 40, 60, 220)
        )
        
        # Add rect attribute for compatibility
        self.main_panel.rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        # Debug check
        print(f"Main panel initialized with rect: {self.main_panel.rect}")
        
        self.ui_elements.append(self.main_panel)
        
        # Title
        self.title_label = Label(
            x=panel_x + panel_width // 2,
            y=panel_y + 30,
            text="LOAD GAME",
            font_size=36,
            color=(255, 255, 255),
            centered=True,
            width=150,
            height=40
        )
        self.labels.append(self.title_label)
        self.ui_elements.append(self.title_label)
        
        # Empty state message (if no saves)
        if not self.saves:
            self.empty_label = Label(
                x=panel_x + panel_width // 2,
                y=panel_y + panel_height // 2,
                text="No save files found",
                font_size=24,
                color=(180, 180, 180),
                centered=True,
                width=300,
                height=30
            )
            self.labels.append(self.empty_label)
            self.ui_elements.append(self.empty_label)
        
        # Create save panels
        content_x = panel_x + 40
        content_y = panel_y + 80
        content_width = panel_width - 80
        self._create_save_panels(content_x, content_y, content_width)
        
        # Create navigation buttons
        button_width = 120
        button_height = 40
        button_y = panel_y + panel_height - 60
        
        # Load button (disabled by default)
        self.load_btn = Button(
            x=panel_x + panel_width // 3 - button_width // 2,
            y=button_y,
            width=button_width,
            height=button_height,
            text="Load",
            on_click=self._on_load_click,
            color=(60, 60, 80)  # Darker color when disabled
        )
        self.buttons.append(self.load_btn)
        self.ui_elements.append(self.load_btn)
        
        # Cancel button
        self.cancel_btn = Button(
            x=panel_x + panel_width * 2 // 3 - button_width // 2,
            y=button_y,
            width=button_width,
            height=button_height,
            text="Cancel",
            on_click=self._on_cancel_click
        )
        self.buttons.append(self.cancel_btn)
        self.ui_elements.append(self.cancel_btn)
        
        # Calculate max scroll
        if self.saves:
            # Max scroll is the bottom of the last save panel minus the visible content height
            visible_height = panel_height - 160  # Subtract header and footer space
            last_panel_bottom = content_y + (len(self.saves) * 110)
            self.max_scroll = max(0, last_panel_bottom - (content_y + visible_height))
        
    def _create_save_panels(self, content_x, content_y, content_width):
        """Create panels for each save file."""
        self.save_panels = []
        
        panel_height = 100
        panel_spacing = 10
        
        for i, save in enumerate(self.saves):
            panel_y = content_y + (i * (panel_height + panel_spacing))
            
            # Create panel for this save
            save_panel = {
                "save": save,
                "rect": pygame.Rect(content_x, panel_y, content_width, panel_height),
                "selected": False
            }
            self.save_panels.append(save_panel)
    
    def update(self, dt):
        """Update menu logic."""
        # Update UI elements
        for ui_element in self.ui_elements:
            if hasattr(ui_element, 'update'):
                ui_element.update(dt)
                
        # Update load button state based on selection
        if self.selected_save:
            self.load_btn.color = (60, 80, 140)  # Enabled color
        else:
            self.load_btn.color = (60, 60, 80)  # Disabled color
        
    def draw(self, screen):
        """Draw the menu."""
        # Draw semi-transparent background
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        
        # Draw UI elements
        for ui_element in self.ui_elements:
            ui_element.draw(screen)
            
        # Draw save panels
        if self.saves:
            font = pygame.font.SysFont(None, 24)
            small_font = pygame.font.SysFont(None, 18)
            
            # Get main panel position for clipping
            panel_x = self.main_panel.rect.x
            panel_y = self.main_panel.rect.y
            panel_width = self.main_panel.width
            panel_height = self.main_panel.height
            
            print(f"Main panel position: {panel_x}, {panel_y}, width: {panel_width}, height: {panel_height}")
            
            # Create a clipping rect for content area
            content_area = pygame.Rect(
                panel_x + 40,
                panel_y + 80,
                panel_width - 80,
                panel_height - 160
            )
            
            print(f"Content area for clipping: {content_area}")
            print(f"Found {len(self.save_panels)} save panels to render")
            
            # Save current clip area
            old_clip = screen.get_clip()
            screen.set_clip(content_area)
            
            # If debug, draw the content area rectangle
            pygame.draw.rect(screen, (100, 100, 160, 80), content_area, width=1)
            
            for panel in self.save_panels:
                # Adjust position for scrolling
                rect = panel["rect"].copy()
                rect.y -= self.scroll_offset
                
                # Skip if completely outside visible area
                if rect.bottom < content_area.top or rect.top > content_area.bottom:
                    continue
                
                save = panel["save"]
                print(f"Drawing save panel at {rect}, save: {save.path}")
                
                # Draw panel background
                if panel["selected"]:
                    pygame.draw.rect(screen, (60, 80, 120), rect, border_radius=5)
                    pygame.draw.rect(screen, (80, 100, 160), rect, width=2, border_radius=5)
                else:
                    pygame.draw.rect(screen, (50, 50, 70), rect, border_radius=5)
                    pygame.draw.rect(screen, (70, 70, 100), rect, width=1, border_radius=5)
                
                # Draw save info
                
                # Draw character name and level - ensure we have valid data
                summary = save.summary if hasattr(save, 'summary') else f"{save.character_name} - Level {save.character_level}"
                name_text = font.render(summary, True, (220, 220, 255))
                screen.blit(name_text, (rect.x + 20, rect.y + 15))
                
                # Draw location
                location = save.location if save.location else "Unknown Location"
                location_text = small_font.render(f"Location: {location}", True, (180, 180, 220))
                screen.blit(location_text, (rect.x + 20, rect.y + 45))
                
                # Draw timestamp
                timestamp = save.formatted_timestamp if hasattr(save, 'formatted_timestamp') else "Unknown Date"
                time_text = small_font.render(f"Saved: {timestamp}", True, (160, 160, 200))
                screen.blit(time_text, (rect.x + 20, rect.y + 70))
                
                # Draw class icon or character thumbnail (placeholder)
                icon_rect = pygame.Rect(rect.right - 90, rect.y + 10, 80, 80)
                pygame.draw.rect(screen, (40, 40, 60), icon_rect, border_radius=5)
                
                # Draw class name in the icon
                class_name = save.character_class if save.character_class else "Unknown Class"
                class_text = small_font.render(class_name, True, (200, 200, 240))
                text_x = icon_rect.x + (icon_rect.width - class_text.get_width()) // 2
                text_y = icon_rect.y + (icon_rect.height - class_text.get_height()) // 2
                screen.blit(class_text, (text_x, text_y))
            
            # Restore original clip area
            screen.set_clip(old_clip)
            
            # Draw scrollbar if needed
            if self.max_scroll > 0:
                scrollbar_height = max(50, content_area.height * (content_area.height / (content_area.height + self.max_scroll)))
                scrollbar_y = content_area.y + (content_area.height - scrollbar_height) * (self.scroll_offset / self.max_scroll)
                scrollbar_rect = pygame.Rect(content_area.right - 10, scrollbar_y, 6, scrollbar_height)
                pygame.draw.rect(screen, (100, 100, 140, 160), scrollbar_rect, border_radius=3)
        
    def handle_event(self, event):
        """Handle input events."""
        # Handle scrolling
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset - event.y * 30))
            return True
            
        # Handle mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            # Check if clicked on a save panel
            mouse_pos = event.pos
            
            for panel in self.save_panels:
                rect = panel["rect"].copy()
                rect.y -= self.scroll_offset  # Adjust for scrolling
                
                if rect.collidepoint(mouse_pos):
                    # Select this save
                    self._select_save(panel["save"])
                    return True
        
        # Pass event to UI elements
        for ui_element in self.ui_elements:
            if hasattr(ui_element, 'handle_event') and ui_element.handle_event(event):
                return True
                
        return False
    
    def _select_save(self, save):
        """Select a save file."""
        self.selected_save = save
        
        # Update panel selection state
        for panel in self.save_panels:
            panel["selected"] = (panel["save"] == save)
    
    def _on_load_click(self):
        """Handle the load button click."""
        if self.selected_save and self.on_save_selected:
            save_data = {
                "path": self.selected_save.path,
                "name": self.selected_save.character_name,
                "data": self.selected_save.data
            }
            self.on_save_selected(save_data)
    
    def _on_cancel_click(self):
        """Handle the cancel button click."""
        if self.on_cancel:
            self.on_cancel() 