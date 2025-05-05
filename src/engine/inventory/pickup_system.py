# src/engine/inventory/pickup_system.py
from typing import List, Optional, Tuple
import pygame
import math
from .items import Item, ItemDatabase
from .inventory import Inventory

class DroppedItem:
    def __init__(self, 
                 item: Item,
                 position: Tuple[float, float],
                 quantity: int = 1):
        self.item = item
        self.position = position
        self.quantity = quantity
        self.pickup_radius = 50.0  # Pixels
        self.floating_offset = 0.0
        self.float_speed = 2.0
        
    def update(self, dt: float):
        # Make item float up and down
        self.floating_offset = math.sin(pygame.time.get_ticks() * 0.003) * 5
        
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[float, float]):
        screen_pos = (
            self.position[0] - camera_offset[0],
            self.position[1] - camera_offset[1] + self.floating_offset
        )
        
        # Draw item icon
        icon = pygame.image.load(self.item.icon_path)
        icon = pygame.transform.scale(icon, (32, 32))
        surface.blit(icon, screen_pos)
        
        # Draw quantity if more than 1
        if self.quantity > 1:
            font = pygame.font.Font(None, 20)
            quantity_text = font.render(str(self.quantity), True, (255, 255, 255))
            surface.blit(quantity_text, 
                        (screen_pos[0] + 20, screen_pos[1] + 20))

class PickupSystem:
    def __init__(self, item_database: ItemDatabase):
        self.item_database = item_database
        self.dropped_items: List[DroppedItem] = []
        
    def spawn_item(self, 
                  item_id: str, 
                  position: Tuple[float, float],
                  quantity: int = 1) -> bool:
        item = self.item_database.get_item(item_id)
        if not item:
            return False
            
        self.dropped_items.append(DroppedItem(item, position, quantity))
        return True
        
    def update(self, dt: float, player_pos: Tuple[float, float], player_inventory: Inventory):
        # Update floating animation
        for item in self.dropped_items:
            item.update(dt)
            
        # Check for pickups
        remaining_items: List[DroppedItem] = []
        for item in self.dropped_items:
            distance = math.sqrt(
                (item.position[0] - player_pos[0]) ** 2 +
                (item.position[1] - player_pos[1]) ** 2
            )
            
            if distance <= item.pickup_radius:
                # Try to add to inventory
                remaining = player_inventory.add_item(item.item, item.quantity)
                if remaining > 0:
                    # Couldn't pick up everything
                    item.quantity = remaining
                    remaining_items.append(item)
            else:
                remaining_items.append(item)
                
        self.dropped_items = remaining_items
        
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[float, float]):
        for item in self.dropped_items:
            item.draw(surface, camera_offset)