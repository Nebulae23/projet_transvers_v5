# src/engine/inventory/inventory.py
from typing import Dict, List, Optional, Tuple
from .items import Item, ItemType

class InventorySlot:
    def __init__(self, item: Optional[Item] = None, quantity: int = 0):
        self.item = item
        self.quantity = quantity
        
    def can_add(self, item: Item, amount: int = 1) -> bool:
        if not self.item:
            return True
        return (self.item.id == item.id and 
                self.item.stackable and 
                self.quantity + amount <= self.item.max_stack)
        
    def add(self, item: Item, amount: int = 1) -> int:
        if not self.item:
            self.item = item
            self.quantity = min(amount, item.max_stack)
            return amount - self.quantity
        
        if self.item.id == item.id and self.item.stackable:
            space_left = self.item.max_stack - self.quantity
            added = min(amount, space_left)
            self.quantity += added
            return amount - added
        
        return amount
    
    def remove(self, amount: int = 1) -> int:
        if not self.item:
            return 0
            
        removed = min(amount, self.quantity)
        self.quantity -= removed
        
        if self.quantity <= 0:
            self.item = None
            self.quantity = 0
            
        return removed

class EquipmentSlots:
    def __init__(self):
        self.slots = {
            "weapon": None,
            "armor": None,
            "accessory": None
        }
        
    def can_equip(self, item: Item, slot: str) -> bool:
        if slot not in self.slots:
            return False
            
        if slot == "weapon" and item.type != ItemType.WEAPON:
            return False
        if slot == "armor" and item.type != ItemType.ARMOR:
            return False
            
        return True
        
    def equip(self, item: Item, slot: str) -> Optional[Item]:
        if not self.can_equip(item, slot):
            return None
            
        old_item = self.slots[slot]
        self.slots[slot] = item
        return old_item
        
    def unequip(self, slot: str) -> Optional[Item]:
        if slot not in self.slots:
            return None
            
        item = self.slots[slot]
        self.slots[slot] = None
        return item

class Inventory:
    def __init__(self, size: int = 20):
        self.size = size
        self.slots: List[InventorySlot] = [InventorySlot() for _ in range(size)]
        self.equipment = EquipmentSlots()
        
    def find_slot(self, item: Item) -> Optional[int]:
        # First try to find a stack that can accept the item
        if item.stackable:
            for i, slot in enumerate(self.slots):
                if slot.can_add(item):
                    return i
                    
        # Then try to find an empty slot
        for i, slot in enumerate(self.slots):
            if not slot.item:
                return i
                
        return None
        
    def add_item(self, item: Item, amount: int = 1) -> int:
        remaining = amount
        
        while remaining > 0:
            slot_index = self.find_slot(item)
            if slot_index is None:
                break
                
            remaining = self.slots[slot_index].add(item, remaining)
            
        return remaining
        
    def remove_item(self, item_id: str, amount: int = 1) -> int:
        removed = 0
        
        for slot in self.slots:
            if not slot.item or slot.item.id != item_id:
                continue
                
            removed += slot.remove(amount - removed)
            if removed >= amount:
                break
                
        return removed
        
    def get_item_count(self, item_id: str) -> int:
        return sum(
            slot.quantity 
            for slot in self.slots 
            if slot.item and slot.item.id == item_id
        )