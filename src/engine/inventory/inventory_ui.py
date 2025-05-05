# src/engine/inventory/inventory_ui.py
import pygame
from typing import Tuple, Optional, List
from ..ui.ui_base import UIElement, UIElementType, TextElement
from ..ui.layout import Layout, LayoutType
from .inventory import Inventory, InventorySlot
from .items import Item

class ItemSlotUI(UIElement):
    def __init__(self, 
                 position: Tuple[int, int],
                 size: Tuple[int, int],
                 slot: InventorySlot):
        super().__init__(position, size, UIElementType.CONTAINER)
        self.slot = slot
        self.selected = False
        self.set_border((128, 128, 128), 1)
        
    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        
        if self.selected:
            pygame.draw.rect(surface, (255, 255, 0), 
                           (*self.position, *self.size), 2)
            
        if self.slot.item:
            # Draw item icon
            icon = pygame.image.load(self.slot.item.icon_path)
            icon = pygame.transform.scale(icon, (self.size[0]-4, self.size[1]-4))
            surface.blit(icon, (self.position[0]+2, self.position[1]+2))
            
            # Draw quantity for stackable items
            if self.slot.quantity > 1:
                font = pygame.font.Font(None, 20)
                quantity_text = font.render(str(self.slot.quantity), True, (255, 255, 255))
                surface.blit(quantity_text, 
                            (self.position[0] + self.size[0] - 20, 
                             self.position[1] + self.size[1] - 20))

class InventoryUI(UIElement):
    def __init__(self, 
                 position: Tuple[int, int],
                 size: Tuple[int, int],
                 inventory: Inventory):
        super().__init__(position, size, UIElementType.CONTAINER)
        self.inventory = inventory
        self.slot_size = (50, 50)
        self.selected_slot: Optional[int] = None
        
        # Create title
        self.title = TextElement(
            (position[0], position[1] - 30),
            "Inventory",
            font_size=24
        )
        self.add_child(self.title)
        
        # Create item slots
        self.slot_uis: List[ItemSlotUI] = []
        self._create_slots()
        
        # Apply grid layout
        self.layout = Layout(self, LayoutType.GRID)
        self.layout.arrange()
        
    def _create_slots(self):
        for i, slot in enumerate(self.inventory.slots):
            slot_ui = ItemSlotUI(
                (0, 0),  # Position will be set by layout
                self.slot_size,
                slot
            )
            self.slot_uis.append(slot_ui)
            self.add_child(slot_ui)
            
    def handle_click(self, position: Tuple[int, int]) -> bool:
        for i, slot_ui in enumerate(self.slot_uis):
            if slot_ui.handle_click(position):
                self._select_slot(i)
                return True
        return False
        
    def _select_slot(self, index: int):
        # Deselect previous slot
        if self.selected_slot is not None:
            self.slot_uis[self.selected_slot].selected = False
            
        # Select new slot
        self.selected_slot = index
        self.slot_uis[index].selected = True
        
    def update(self):
        # Update slot displays
        for slot_ui, inventory_slot in zip(self.slot_uis, self.inventory.slots):
            slot_ui.slot = inventory_slot